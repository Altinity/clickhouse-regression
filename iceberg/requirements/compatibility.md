| Property                                                                                                 | Read support by ClickHouse |
| -------------------------------------------------------------------------------------------------------- | -------------------------- |
| Format Version 1                                                                                         | Yes                        |
| Format Version 2                                                                                         | Yes                        |
| Format Version 3                                                                                         | No                         |
| Position deletes (mark a row deleted by data file path and the row position in the data file)            | No                        |
| Equality deletes (mark a row deleted by one or more column values)                                       | No                        |
| Primitive data types                                                                                     | Yes (except from UUID)     |
| Nested data types                                                                                     | Yes, but struct represented as nested tuples                        |
| Schema evolution: type promotion (int -> long, float -> double, decimal -> decimal with wider precision) |       Yes                     |
| Schema evolution: adding fields                                                                          | Yes                        |
| Schema evolution: renaming fields                                                                        | Yes                        |
| Schema evolution: deleting fields                                                                        | Yes                        |
| Schema evolution: reordering fields                                                                      | Yes                        |
| Partition Transforms                                                                                     |                            |
| Partition Evolution: adding partition spec fields                                                        |                            |
| Partition Evolution: renaming partition spec fields                                                      |                            |
| Partition Evolution: reordering partition spec fields                                                    |                            |
| Partition Evolution: removing partition spec fields                                                      |                            |
| Sorting                                                                                                  |            Not preserved                |
| Point in Time Reads (Time Travel)                                                                        | No                         |
| Writes: Overwrite data                                                                                   | Yes                        |
| Writes: Append data                                                                                      | Yes                        |