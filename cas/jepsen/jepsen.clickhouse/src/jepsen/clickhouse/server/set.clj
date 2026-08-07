(ns jepsen.clickhouse.server.set
  (:require
   [clojure.tools.logging :refer :all]
   [jepsen
    [checker :as checker]
    [client :as client]
    [generator :as gen]]
   [jepsen.clickhouse.server.client :as chc]))

(defrecord SetClient [table-created? node]
  client/Client
  (open! [this test node]
    (assoc this :node node))

  (setup! [this test]
    (locking table-created?
      (when (compare-and-set! table-created? false true)
        (chc/query! node "DROP TABLE IF EXISTS set ON CLUSTER test_cluster")
        ;; Majority quorum so an :ok insert is durable on >1 replica (not only the
        ;; local node under partition). With 3 replicas, 2 is majority.
        (chc/query! node (str "CREATE TABLE set ON CLUSTER test_cluster "
                              "(value Int64) Engine=ReplicatedMergeTree "
                              "ORDER BY value "
                              "SETTINGS storage_policy = 'cas'")))))

  (invoke! [this test op]
    (chc/with-exception op
      (case (:f op)
        :add (do
               (chc/query! node
                           (str "INSERT INTO set "
                                "SETTINGS insert_quorum = 2, insert_quorum_parallel = 0, async_insert = 0 "
                                "VALUES (" (:value op) ")"))
               (assoc op :type :ok))
        :read (do
                ;; After heal, wait for this replica to catch up before checking the set.
                (chc/query! node "SYSTEM SYNC REPLICA set" chc/final-read-timeout)
                (->> (chc/query-lines!
                      node
                      "SELECT value FROM set SETTINGS select_sequential_consistency = 1"
                      chc/final-read-timeout)
                     (mapv #(Long/parseLong %))
                     (assoc op :type :ok, :value))))))

  (teardown! [_ test])

  (close! [_ test]))

(defn workload
  "A generator, client, and checker for a set test."
  [opts]
  {:client    (SetClient. (atom false) nil)
   :checker   (checker/compose
                {:set (checker/set)
                 :perf (checker/perf)})
   :generator (->> (range)
                   (map (fn [x] {:type :invoke, :f :add, :value x})))
   :final-generator (gen/once {:type :invoke, :f :read, :value nil})})
