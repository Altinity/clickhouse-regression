(ns jepsen.clickhouse.server.client
  "HTTP client for ClickHouse server Jepsen tests.

  Uses the HTTP interface instead of JDBC: recent ClickHouse builds are not
  reliably handled by clickhouse-jdbc 0.3.2 (binary framing / Magic errors)."
  (:require [clojure.string :as str]
            [clojure.tools.logging :refer :all]
            [jepsen.util :as util])
  (:import (java.net HttpURLConnection URL)
           (java.io InputStreamReader BufferedReader OutputStreamWriter)))

(def operation-timeout "Default operation timeout in ms" 30000)

(def final-read-timeout "Timeout for post-heal sync + final read" 120000)

(defn indeterminate-error?
  "True when the outcome of the op is unknown (timeout / transport), not a
  definitive ClickHouse rejection. Public so `with-exception` can expand in
  other namespaces.

  Do not treat HTTP 5xx with a ClickHouse `Code:` body as indeterminate — that
  is a definitive server rejection (e.g. UNSUPPORTED_PARAMETER)."
  [^String message]
  (let [m (or message "")]
    (boolean
     (and (not (re-find #"(?m)^(?:HTTP \d+ from [^:]+: )?Code:\s*\d+" m))
          (re-find
           #"(?i)timed?\s*out|timeout|Connection refused|Connection reset|Broken pipe|ConnectException|SocketTimeout|UnknownHost|No route to host|Pipe closed"
           m)))))

(defn- read-stream
  [stream]
  (if-not stream
    ""
    (with-open [r (BufferedReader. (InputStreamReader. stream "UTF-8"))]
      (loop [sb (StringBuilder.)]
        (if-let [line (.readLine r)]
          (do (.append sb line) (.append sb \newline) (recur sb))
          (str sb))))))

(defn query!
  "POST `sql` to ClickHouse HTTP on `node`. Returns response body.
   Throws on HTTP errors or ClickHouse exception payloads.
   Optional `timeout-ms` overrides the default operation timeout."
  ([node sql]
   (query! node sql operation-timeout))
  ([node sql timeout-ms]
   (util/timeout timeout-ms
                 (throw (RuntimeException. (str "HTTP query to " node " timed out")))
                 (let [url (URL. (str "http://" (name node) ":8123/?default_format=TabSeparated"))
                       ^HttpURLConnection conn (doto ^HttpURLConnection (.openConnection url)
                                                 (.setRequestMethod "POST")
                                                 (.setDoOutput true)
                                                 (.setConnectTimeout timeout-ms)
                                                 (.setReadTimeout timeout-ms)
                                                 (.setRequestProperty "Content-Type" "text/plain; charset=UTF-8"))]
                   (try
                     (with-open [w (OutputStreamWriter. (.getOutputStream conn) "UTF-8")]
                       (.write w ^String sql))
                     (let [code (.getResponseCode conn)
                           body (read-stream (if (>= code 400)
                                               (.getErrorStream conn)
                                               (.getInputStream conn)))]
                       (when (>= code 400)
                         (throw (RuntimeException. (str "HTTP " code " from " node ": " (str/trim body)))))
                       ;; Some CH versions still return 200 with an exception body.
                       (when (re-find #"(?m)^Code:\s*\d+" body)
                         (throw (RuntimeException. (str "ClickHouse error from " node ": " (str/trim body)))))
                       body)
                     (finally
                       (.disconnect conn)))))))

(defn query-lines!
  "Like `query!`, but returns non-blank response lines."
  ([node sql]
   (query-lines! node sql operation-timeout))
  ([node sql timeout-ms]
   (->> (query! node sql timeout-ms)
        str/split-lines
        (remove str/blank?)
        vec)))

(defn ping!
  "Cheap liveness check."
  [node]
  (query! node "SELECT 1")
  true)

(defmacro with-exception
  "Takes an operation and a body. Evaluates body, catches exceptions, and maps
  them to ops with :type :fail (definitive rejection) or :type :info
  (indeterminate: timeout / connection loss)."
  [op & body]
  `(try ~@body
        (catch Exception e#
          (let [message# (or (.getMessage e#) "")]
            (if (indeterminate-error? message#)
              (assoc ~op :type :info, :error message#)
              (assoc ~op :type :fail, :error message#))))))
