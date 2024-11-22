# Table of Contents

- [Comparison Table of Native Reader Performance](#comparison-table-of-native-reader-performance)
- [Charts](#charts)

# Comparison Table of Native Reader Performance

**Dataset:** https://datasets.clickhouse.com/hits_compatible/hits.parquet

**Rows:** `100 000 000`

**File type:** single parquet

The table below represents the comparison of the performance of the same queries between `native parquet reader` and the `regular parquet reader`.

Each query was executed three times, and the results of each run are presented in the table below.

The queries with their corresponding IDs can be found [here](https://github.com/Altinity/clickhouse-regression/blob/run_bloom_filter_tests/parquet/performance/results/native_reader/queries/queries.md).

| Native Reader | Query ID | Time 0 (Seconds)             | Memory 0 (Bytes) | Time 1 (Seconds)             | Memory 1 (Bytes) | Time 2 (Seconds)             | Memory 2 (Bytes) |
|---------------|----------|--------------------|----------|--------------------|----------|--------------------|----------|
| True          | query_0  | 0.6969590187072754 | 16821032 | 0.7177548408508301 | 16821032 | 0.7146885395050049 | 16821032 |
| False         | query_0  | 0.6015362739562988 | 16821032 | 0.7046184539794922 | 16821032 | 0.635699987411499  | 16821032 |
| True          | query_1  | 0.9303810596466064 | 16821032 | 0.9305911064147949 | 16821032 | 1.0797734260559082 | 16821032 |
| False         | query_1  | 0.8370363712310791 | 16821032 | 0.7264528274536133 | 16821032 | 0.784374475479126  | 16821032 |
| True          | query_2  | 1.1355633735656738 | 16821928 | 0.9143581390380859 | 16821928 | 0.9568731784820557 | 16821928 |
| False         | query_2  | 0.7634892463684082 | 16821928 | 0.7956645488739014 | 16821928 | 0.8908843994140625 | 16821928 |
| True          | query_3  | 1.6716663837432861 | 16821032 | 1.7954044342041016 | 16821032 | 1.6576027870178223 | 16821032 |
| False         | query_3  | 0.9938735961914062 | 16821032 | 0.9253945350646973 | 16821032 | 0.9293172359466553 | 16821032 |
| True          | query_4  | 2.097700595855713  | 16821032 | 2.071321725845337  | 16821032 | 2.1146860122680664 | 16821032 |
| False         | query_4  | 1.3543763160705566 | 16821032 | 1.3537359237670898 | 16821032 | 1.3169939517974854 | 16821032 |
| True          | query_5  | 2.378453254699707  | 16821032 | 2.3442118167877197 | 16821032 | 2.3864126205444336 | 16821032 |
| False         | query_5  | 1.7446420192718506 | 16821032 | 1.7280519008636475 | 16821032 | 1.7042944431304932 | 16821032 |
| True          | query_6  | 0.9339790344238281 | 16821032 | 0.951195240020752  | 16821032 | 0.97989821434021   | 16821032 |
| False         | query_6  | 0.7571983337402344 | 16821032 | 0.7531490325927734 | 16821032 | 0.7606682777404785 | 16821032 |
| True          | query_7  | 1.0248916149139404 | 16821032 | 0.8725428581237793 | 16821032 | 1.0573065280914307 | 16821032 |
| False         | query_7  | 0.7707340717315674 | 16821032 | 0.7676064968109131 | 16821032 | 0.6969935894012451 | 16821032 |
| True          | query_8  | 2.466386556625366  | 16821928 | 2.522296667098999  | 16821928 | 2.425503730773926  | 16821928 |
| False         | query_8  | 1.7287278175354004 | 16821928 | 1.8134198188781738 | 16821928 | 1.8101789951324463 | 16821928 |
| True          | query_9  | 0.9338955879211426 | 16823976 | 0.9360530376434326 | 16823976 | 0.9480109214782715 | 16823976 |
| False         | query_9  | 1.9826726913452148 | 16823976 | 1.9351279735565186 | 16823976 | 2.0143237113952637 | 16823976 |
| True          | query_10 | 1.8592536449432373 | 16821928 | 1.906087875366211  | 16821928 | 1.8454856872558594 | 16821928 |
| False         | query_10 | 1.3582119941711426 | 16821928 | 1.2974262237548828 | 16821928 | 1.3056623935699463 | 16821928 |
| True          | query_11 | 1.005413293838501  | 16823208 | 0.9191298484802246 | 16823208 | 0.9711008071899414 | 16823208 |
| False         | query_11 | 1.297727346420288  | 16823208 | 1.2909622192382812 | 16823208 | 1.345094919204712  | 16823208 |
| True          | query_12 | 2.694427967071533  | 16821032 | 2.4201602935791016 | 16821032 | 2.5625762939453125 | 16821032 |
| False         | query_12 | 2.1002132892608643 | 16821032 | 1.9552085399627686 | 16821032 | 2.045646905899048  | 16821032 |
| True          | query_13 | 2.950251817703247  | 16821928 | 3.0045249462127686 | 16821928 | 3.2354066371917725 | 16821928 |
| False         | query_13 | 2.6138756275177    | 16821928 | 2.4410438537597656 | 16821928 | 2.6609528064727783 | 16821928 |
| True          | query_14 | 1.1101493835449219 | 16821928 | 1.06913423538208   | 16821928 | 1.0042719841003418 | 16821928 |
| False         | query_14 | 2.2082247734069824 | 16821928 | 2.209164619445801  | 16821928 | 2.1200015544891357 | 16821928 |
| True          | query_15 | 2.4423625469207764 | 16821032 | 2.3945586681365967 | 16821032 | 2.4239397048950195 | 16821032 |
| False         | query_15 | 1.6155037879943848 | 16821032 | 1.673156976699829  | 16821032 | 1.6285412311553955 | 16821032 |
| True          | query_16 | 4.438088893890381  | 16821928 | 4.507529258728027  | 16821928 | 4.536947965621948  | 16821928 |
| False         | query_16 | 3.8189542293548584 | 16821928 | 3.6991055011749268 | 16821928 | 3.903766632080078  | 16821928 |
| True          | query_17 | 3.6920011043548584 | 16821928 | 3.6930689811706543 | 16821928 | 3.6741669178009033 | 16821928 |
| False         | query_17 | 3.034173011779785  | 16821928 | 2.9144716262817383 | 16821928 | 3.0793278217315674 | 16821928 |
| True          | query_18 | 7.89959716796875   | 16823208 | 7.851152658462524  | 16823208 | 7.762021541595459  | 16823208 |
| False         | query_18 | 7.047718048095703  | 16823208 | 6.911838054656982  | 16823208 | 7.035710573196411  | 16823208 |
| True          | query_19 | 1.5261526107788086 | 16821032 | 1.617201805114746  | 16821032 | 1.5425150394439697 | 16821032 |
| False         | query_19 | 0.8858630657196045 | 16821032 | 0.8105359077453613 | 16821032 | 0.8411693572998047 | 16821032 |
| True          | query_20 | 3.957897663116455  | 16821032 | 4.104811906814575  | 16821032 | 3.71004056930542   | 16821032 |
| False         | query_20 | 4.437343120574951  | 16821032 | 4.697883129119873  | 16821032 | 4.527829647064209  | 16821032 |
| True          | query_21 | 3.9631831645965576 | 16821928 | 4.201467990875244  | 16821928 | 3.9530436992645264 | 16821928 |
| False         | query_21 | 5.311370611190796  | 16821928 | 4.710474252700806  | 16821928 | 4.932651519775391  | 16821928 |
| True          | query_22 | 5.5586442947387695 | 16823976 | 5.657460689544678  | 16823976 | 5.942174196243286  | 16823976 |
| False         | query_22 | 8.32521939277649   | 16823976 | 7.986260652542114  | 16823976 | 8.34261417388916   | 16823976 |
| True          | query_23 | 1.7225313186645508 | 21048600 | 1.6036028861999512 | 21048600 | 1.7464625835418701 | 21048600 |
| False         | query_23 | 21.3783962726593   | 21048600 | 21.25403118133545  | 21048600 | 22.298691272735596 | 21048600 |
| True          | query_24 | 2.1346662044525146 | 16821928 | 2.101935863494873  | 16821928 | 2.17741060256958   | 16821928 |
| False         | query_24 | 1.8695950508117676 | 16821928 | 1.844963788986206  | 16821928 | 1.8324646949768066 | 16821928 |
| True          | query_25 | 1.8918488025665283 | 16821032 | 1.9394145011901855 | 16821032 | 1.8465876579284668 | 16821032 |
| False         | query_25 | 1.373159646987915  | 16821032 | 1.3249506950378418 | 16821032 | 1.402803897857666  | 16821032 |
| True          | query_26 | 2.1157002449035645 | 16821928 | 2.1704695224761963 | 16821928 | 2.27347731590271   | 16821928 |
| False         | query_26 | 1.9632899761199951 | 16821928 | 1.6802408695220947 | 16821928 | 1.8268792629241943 | 16821928 |
| True          | query_27 | 3.7016053199768066 | 16821928 | 3.851496934890747  | 16821928 | 3.68499493598938   | 16821928 |
| False         | query_27 | 4.53217077255249   | 16821928 | 4.9457173347473145 | 16821928 | 4.7908337116241455 | 16821928 |
| True          | query_28 | 15.644773721694946 | 16821032 | 14.924829483032227 | 16821032 | 15.174883127212524 | 16821032 |
| False         | query_28 | 15.71343445777893  | 16821032 | 15.10931944847107  | 16821032 | 15.43964409828186  | 16821032 |
| True          | query_29 | 0.9815573692321777 | 16823080 | 1.0472784042358398 | 16823080 | 1.0126090049743652 | 16823080 |
| False         | query_29 | 0.7995483875274658 | 16823080 | 0.8180203437805176 | 16823080 | 0.7422363758087158 | 16823080 |
| True          | query_30 | 0.9419379234313965 | 16825000 | 0.9949803352355957 | 16825000 | 1.0450127124786377 | 16825000 |
| False         | query_30 | 2.05078387260437   | 16825000 | 2.050043821334839  | 16825000 | 2.1176795959472656 | 16825000 |
| True          | query_31 | 1.073779821395874  | 16825000 | 1.0941669940948486 | 16825000 | 0.9484691619873047 | 16825000 |
| False         | query_31 | 2.8870320320129395 | 16825000 | 2.6743388175964355 | 16825000 | 2.7964727878570557 | 16825000 |
| True          | query_32 | 0.9584336280822754 | 16823976 | 0.9962036609649658 | 16823976 | 0.9437699317932129 | 16823976 |
| False         | query_32 | 7.28498649597168   | 16823976 | 7.203861951828003  | 16823976 | 7.121806859970093  | 16823976 |
| True          | query_33 | 6.395413398742676  | 16821032 | 6.280280828475952  | 16821032 | 6.905294418334961  | 16821032 |
| False         | query_33 | 7.248021125793457  | 16821032 | 7.1789374351501465 | 16821032 | 7.4908952713012695 | 16821032 |
| True          | query_34 | 6.368836879730225  | 16821032 | 6.335352659225464  | 16821032 | 6.603154182434082  | 16821032 |
| False         | query_34 | 7.520913362503052  | 16821032 | 7.05668044090271   | 16821032 | 7.557462453842163  | 16821032 |
| True          | query_35 | 2.2707319259643555 | 16821032 | 2.2117600440979004 | 16821032 | 2.200141668319702  | 16821032 |
| False         | query_35 | 1.6424593925476074 | 16821032 | 1.5247564315795898 | 16821032 | 1.5250358581542969 | 16821032 |
| True          | query_36 | 0.8760135173797607 | 16825000 | 0.9327003955841064 | 16825000 | 0.8069372177124023 | 16825000 |
| False         | query_36 | 0.8679952621459961 | 16825000 | 1.004528284072876  | 16825000 | 0.9850358963012695 | 16825000 |
| True          | query_37 | 0.8611023426055908 | 16825000 | 0.8964910507202148 | 16825000 | 0.8571743965148926 | 16825000 |
| False         | query_37 | 0.8761742115020752 | 16825000 | 0.8532617092132568 | 16825000 | 0.9496283531188965 | 16825000 |
| True          | query_38 | 0.872666597366333  | 16826408 | 0.8875312805175781 | 16826408 | 0.8745834827423096 | 16826408 |
| False         | query_38 | 0.9237377643585205 | 16826408 | 0.9483535289764404 | 16826408 | 0.9547555446624756 | 16826408 |
| True          | query_39 | 0.9180247783660889 | 16827944 | 0.9258944988250732 | 16827944 | 0.8892874717712402 | 16827944 |
| False         | query_39 | 1.260491132736206  | 16827944 | 1.1306846141815186 | 16827944 | 1.165597677230835  | 16827944 |
| True          | query_40 | 0.9303276538848877 | 16826408 | 0.9265153408050537 | 16826408 | 0.8570261001586914 | 16826408 |
| False         | query_40 | 0.8065836429595947 | 16826408 | 0.8575839996337891 | 16826408 | 0.7369353771209717 | 16826408 |
| True          | query_41 | 0.8809561729431152 | 16827432 | 0.8951554298400879 | 16827432 | 0.8653810024261475 | 16827432 |
| False         | query_41 | 0.7866940498352051 | 16827432 | 0.7072455883026123 | 16827432 | 0.6724159717559814 | 16827432 |
| True          | query_42 | 0.8948886394500732 | 16825000 | 0.9026377201080322 | 16825000 | 0.9086430072784424 | 16825000 |
| False         | query_42 | 0.7414147853851318 | 16825000 | 0.7659671306610107 | 16825000 | 0.8209681510925293 | 16825000 |

# Charts

<img src="https://github.com/user-attachments/assets/89ec4dd6-67f1-44b3-b985-14b7a9ee3d03" alt="queryquery0 comparison"></img> <img src="https://github.com/user-attachments/assets/17f2c225-9dbc-4fdd-b465-6d1a71db68f5" alt="queryquery1 comparison"></img> <img src="https://github.com/user-attachments/assets/4e4045ee-0403-4c7c-8753-d38de80e77ec" alt="queryquery2 comparison"></img> <img src="https://github.com/user-attachments/assets/5c3c9ff6-33b2-4764-9572-33a72672e10c" alt="queryquery3 comparison"></img> <img src="https://github.com/user-attachments/assets/96ec22e6-6a84-4875-a58d-407b4f73cce4" alt="queryquery4 comparison"></img> <img src="https://github.com/user-attachments/assets/833dd073-cdb2-4883-98ec-0ba67f151455" alt="queryquery5 comparison"></img> <img src="https://github.com/user-attachments/assets/44235e50-0cbb-44c2-a323-f05fa0b1d2db" alt="queryquery6 comparison"></img> <img src="https://github.com/user-attachments/assets/addaf20b-ba37-4c0c-b7af-460ad7668128" alt="queryquery7 comparison"></img> <img src="https://github.com/user-attachments/assets/cf7577d8-6b4d-4a35-b9d4-1d279213c39c" alt="queryquery8 comparison"></img> <img src="https://github.com/user-attachments/assets/2ca331af-2d3d-4e5f-a7a0-b4789759ea05" alt="queryquery9 comparison"></img> <img src="https://github.com/user-attachments/assets/fe42e177-5452-4b16-b0b1-c7709b66163f" alt="queryquery10 comparison"></img> <img src="https://github.com/user-attachments/assets/3ccfb9c1-34bd-4457-a112-138878257545" alt="queryquery11 comparison"></img> <img src="https://github.com/user-attachments/assets/0fa60add-b81b-4722-885f-939722d770a3" alt="queryquery12 comparison"></img> <img src="https://github.com/user-attachments/assets/0ef0b49b-8009-4f9b-9369-fa1d7469eb8a" alt="queryquery13 comparison"></img> <img src="https://github.com/user-attachments/assets/35428af0-d0b2-40d4-8ea2-10cfcfec74b5" alt="queryquery14 comparison"></img> <img src="https://github.com/user-attachments/assets/18ae9fd7-22e4-4d7c-9185-5a49a669521e" alt="queryquery15 comparison"></img> <img src="https://github.com/user-attachments/assets/f25f804a-e7de-4e24-9b13-2fce44ca29da" alt="queryquery16 comparison"></img> <img src="https://github.com/user-attachments/assets/3f756409-fe1c-479e-969d-a36667d7672b" alt="queryquery17 comparison"></img> <img src="https://github.com/user-attachments/assets/8afdc602-eeea-4693-8c7b-5f46fd4480af" alt="queryquery18 comparison"></img> <img src="https://github.com/user-attachments/assets/6b5431c3-75de-40d1-9848-cfe92c66d1c7" alt="queryquery19 comparison"></img> <img src="https://github.com/user-attachments/assets/425e2705-72e5-4744-97cb-81b78694f1fc" alt="queryquery20 comparison"></img> <img src="https://github.com/user-attachments/assets/47523a24-de13-4a2b-9490-47439482b5d6" alt="queryquery21 comparison"></img> <img src="https://github.com/user-attachments/assets/850add61-1dfa-488d-b9a1-1eca671b3295" alt="queryquery22 comparison"></img> <img src="https://github.com/user-attachments/assets/c828be64-6cc1-49ef-9d5e-55b26d5b5f08" alt="queryquery23 comparison"></img> <img src="https://github.com/user-attachments/assets/3bcb1de3-a6c6-429e-a9c4-f013256bb0f7" alt="queryquery24 comparison"></img> <img src="https://github.com/user-attachments/assets/e1311f89-1c62-41a1-bfe1-bc0598381514" alt="queryquery25 comparison"></img> <img src="https://github.com/user-attachments/assets/5a7f245a-bd1c-413f-a3d7-dbb21b4d8ee3" alt="queryquery26 comparison"></img> <img src="https://github.com/user-attachments/assets/2bc50d5b-4802-442c-bf9d-26cbc1f51d21" alt="queryquery27 comparison"></img> <img src="https://github.com/user-attachments/assets/c6357125-f29f-4f97-ae15-e6b0e860d898" alt="queryquery28 comparison"></img> <img src="https://github.com/user-attachments/assets/e1f39ebd-554a-4195-8b27-6a836955545f" alt="queryquery29 comparison"></img> <img src="https://github.com/user-attachments/assets/fbc49786-8953-4008-9681-9a47a51677b0" alt="queryquery30 comparison"></img> <img src="https://github.com/user-attachments/assets/72f75afe-39e5-43d8-a849-94866000a2b3" alt="queryquery31 comparison"></img> <img src="https://github.com/user-attachments/assets/8ea86677-8dd3-4f04-9216-7d72c7cc27b6" alt="queryquery32 comparison"></img> <img src="https://github.com/user-attachments/assets/780f9411-c593-4521-9fe8-63c19bfbcb1b" alt="queryquery33 comparison"></img> <img src="https://github.com/user-attachments/assets/7446b3a9-0c4c-4775-b0d0-e00cf8bace9a" alt="queryquery34 comparison"></img> <img src="https://github.com/user-attachments/assets/2fbb67dc-8d2c-4764-875e-adeb647f585b" alt="queryquery35 comparison"></img> <img src="https://github.com/user-attachments/assets/76d23096-2984-4d12-8d8d-6a8296c0aae7" alt="queryquery36 comparison"></img> <img src="https://github.com/user-attachments/assets/e0c9b947-21f5-4678-93c6-dea550f720df" alt="queryquery37 comparison"></img> <img src="https://github.com/user-attachments/assets/a4d2e365-51da-4b91-8c21-d5e95dcc0116" alt="queryquery38 comparison"></img> <img src="https://github.com/user-attachments/assets/23cc6b8e-a20c-4b79-9a38-41e1ab77ef5d" alt="queryquery39 comparison"></img> <img src="https://github.com/user-attachments/assets/8dd76373-ab84-4b36-987a-55c28fe8218b" alt="queryquery40 comparison"></img> <img src="https://github.com/user-attachments/assets/c0a569ed-b776-4645-96e9-f8989420c49e" alt="queryquery41 comparison"></img>

