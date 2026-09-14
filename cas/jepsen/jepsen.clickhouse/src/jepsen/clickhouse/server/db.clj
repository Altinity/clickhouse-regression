(ns jepsen.control.scp)

;; We need to overwrite Jepsen's implementation of scp! because it
;; doesn't use strict-host-key-checking

(defn scp!
  "Runs an SCP command by shelling out. Takes a conn-spec (used for port, key,
  etc), a seq of sources, and a single destination, all as strings."
  [conn-spec sources dest]
  (apply util/sh "scp" "-rpC"
         "-P" (str (:port conn-spec))
         (concat (when-let [k (:private-key-path conn-spec)]
                   ["-i" k])
                 (if-not (:strict-host-key-checking conn-spec)
                   ["-o StrictHostKeyChecking=no"])
                 sources
                 [dest]))
  nil)

(ns jepsen.clickhouse.keeper.db)

(ns jepsen.clickhouse.server.db
  (:require [clojure.tools.logging :refer :all]
            [clojure.java.io :as io]
            [clojure.string :as str]
            [zookeeper :as zk]
            [jepsen
             [control :as c]
             [store :as store]
             [core :as core]
             [os :as os]
             [db :as db]]
            [jepsen.control.util :as cu]
            [jepsen.clickhouse.constants :refer :all]
            [jepsen.clickhouse.server.utils :refer :all]
            [jepsen.clickhouse.keeper.utils :as keeperutils]
            [jepsen.clickhouse.utils :as chu]))

(defn replicated-merge-tree-config
  [test node config-template]
  (let [nodes (:nodes test)
        replacement-map {#"\{server1\}" (get nodes 0)
                         #"\{server2\}" (get nodes 1)
                         #"\{server3\}" (get nodes 2)
                         #"\{keeper\}" (:keeper test)
                         #"\{replica_name\}" node}]
    (reduce #(clojure.string/replace %1 (get %2 0) (get %2 1)) config-template replacement-map)))

(defn content-addressed-storage-config
  [test node config-template]
  ;; server_root_id must be unique per CH process mounting a shared CAS pool.
  ;; Include :cas-run-id so a wiped local uuid (fresh data dir) does not collide with
  ;; a previous run's owner object still present in the pool.
  (let [run-id (or (:cas-run-id test) "run")
        root-id (str (name node) "-" run-id)]
    (clojure.string/replace config-template #"\{server_root_id\}" root-id)))

(defn install-configs
  [test node]
  (c/exec :echo (slurp (io/resource "config.xml")) :> (str configs-dir "/config.xml"))
  (c/exec :echo (slurp (io/resource "users.xml")) :> (str configs-dir "/users.xml"))
  (c/exec :echo (replicated-merge-tree-config test node (slurp (io/resource "replicated_merge_tree.xml"))) :> (str sub-configs-dir "/replicated_merge_tree.xml"))
  (c/exec :echo (content-addressed-storage-config test node (slurp (io/resource "content_addressed_storage.xml"))) :> (str sub-configs-dir "/content_addressed_storage.xml")))

(defn extra-setup
  [test node]
  (do
    (info "Installing configs")
    (install-configs test node)))

(defn keeper-config
  [test node config-template]
  (let [replacement-map {#"\{srv1\}" node}]
    (reduce #(clojure.string/replace %1 (get %2 0) (get %2 1)) config-template replacement-map)))

(defn install-keeper-configs
  [test node]
  (c/exec :echo (keeper-config test node (slurp (io/resource "keeper_config_solo.xml"))) :> (str configs-dir "/keeper_config.xml")))

(defn keeper
  [version reuse-binary]
  (chu/db version reuse-binary keeperutils/start-clickhouse! install-keeper-configs))

(defn snarf-keeper-logs!
  "Downloads Keeper logs"
  [test]
  ; Download logs
  (let [keeper-node (:keeper test)]
    (info "Snarfing Keeper log files")
    (c/on keeper-node
      (doseq [[remote local] (db/log-files-map (:db test) test keeper-node)]
        (when (cu/exists? remote)
          (info "downloading" remote "to" local)
          (try
            (c/download
              remote
              (.getCanonicalPath
                (store/path! test (name keeper-node)
                             ; strip leading /
                             (str/replace local #"^/" ""))))
            (catch java.io.IOException e
              (if (= "Pipe closed" (.getMessage e))
                (info remote "pipe closed")
                (throw e)))
            (catch java.lang.IllegalArgumentException e
              ; This is a jsch bug where the file is just being
              ; created
              (info remote "doesn't exist"))))))))

(defn is-primary
  "Is node primary"
  [test node]
  (= 0 (.indexOf (:nodes test) node)))

(defn zk-connect
  [host port timeout]
  (let [conn (zk/connect (str host ":" port) :timeout-msec timeout)
               sessionId (.getSessionId conn)]
           (when (= -1 sessionId)
             (throw (RuntimeException.
                      (str "Connection to " host " failed"))))
           conn))
  
(defn keeper-alive?
  [node test]
  (info "Checking Keeper alive on" node)
  (try
    ;; Keep alive-check timeout short so a dead/wrong-arch binary fails setup
    ;; in ~minutes instead of hanging ~15m (30 tries × 30s ZK connect).
    ;; Always close the session — Jepsen probes this repeatedly during setup.
    (let [conn (zk-connect (name node) 9181 5000)]
      (try
        true
        (finally
          (try (zk/close conn) (catch Exception _)))))
    (catch Exception _ false)))

(defn db
  [version reuse-binary]
  (reify db/DB
    (setup! [this test node]
      (let [keeper-node (:keeper test)]
        (when (is-primary test node)
          (info (str "Starting Keeper on " keeper-node))
          (c/on keeper-node 
            (os/setup! (:os test) test keeper-node) 
            (db/setup! (keeper version reuse-binary) test keeper-node)))
        (c/su
         (do
           (info "Preparing directories")
           (chu/prepare-dirs)
           (if (or (not (cu/exists? binary-path)) (not reuse-binary))
             (do (info "Downloading clickhouse")
                 (let [clickhouse-path (chu/download-clickhouse version)]
                   (chu/install-downloaded-clickhouse clickhouse-path)))
             (info "Binary already exsist on path" binary-path "skipping download"))
           (extra-setup test node)
           (info "Waiting for Keeper")
           ;; Non-primary nodes race the primary's Keeper install/start; allow
           ;; enough time for download + solo Keeper boot (not just 30s).
           (chu/wait-clickhouse-alive! keeper-node test keeper-alive? :maxtries 180)
           (info "Starting server")
           (start-clickhouse! node test)
           (info "ClickHouse started")))))

    (teardown! [_ test node]
      (let [keeper-node (:keeper test)]
        (when (is-primary test node)
          (info (str "Tearing down Keeper on " keeper-node))
          ;; Both forms must stay inside c/on so OS teardown runs on the Keeper host.
          (c/on keeper-node
            (db/teardown! (keeper version reuse-binary) test keeper-node)
            (os/teardown! (:os test) test keeper-node))))
      (info node "Tearing down clickhouse")
      (c/su
       (chu/kill-clickhouse! node test)
       (if (not reuse-binary)
         (c/exec :rm :-rf binary-path))
       (c/exec :rm :-rf pid-file-path)
       (c/exec :rm :-rf data-dir)
       (c/exec :rm :-rf logs-dir)
       (c/exec :rm :-rf configs-dir)))

    db/LogFiles
    (log-files [_ test node]
      (when (is-primary test node)
        (info "Downloading Keeper logs")
        (snarf-keeper-logs! test))
      (c/su
       (chu/kill-clickhouse! node test)
       (if (cu/exists? data-dir)
         (do
           (info node "Data folder exists, going to compress")
           (c/cd root-folder
            (c/exec :tar :czf "data.tar.gz" "db"))))
       (if (cu/exists? (str logs-dir))
         (do
           (info node "Logs exist, going to compress")
           (c/cd root-folder
                 (c/exec :tar :czf "logs.tar.gz" "logs"))) (info node "Logs are missing")))
      (let [common-logs [(str root-folder "/logs.tar.gz") (str root-folder "/data.tar.gz")]
            gdb-log (str logs-dir "/gdb.log")]
        (if (cu/exists? (str logs-dir "/gdb.log"))
          (conj common-logs gdb-log)
          common-logs)))))
