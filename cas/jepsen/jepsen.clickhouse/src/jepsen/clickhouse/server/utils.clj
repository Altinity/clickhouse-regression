(ns jepsen.clickhouse.server.utils
  (:require [jepsen.clickhouse.utils :as chu]
            [jepsen.clickhouse.constants :refer :all]
            [jepsen.clickhouse.server.client :as chc]
            [clojure.tools.logging :refer :all]))

(defn clickhouse-alive?
  [node test]
  (try
    (chc/ping! node)
    (catch Exception _ false)))

(defn start-clickhouse!
  [node test]
  (chu/start-clickhouse!
    node
    test
    clickhouse-alive?
    :server
    :--config (str configs-dir "/config.xml")
    :--
    :--logger.log (str logs-dir "/clickhouse.log")
    :--logger.errorlog (str logs-dir "/clickhouse.err.log")
    :--path data-dir))
