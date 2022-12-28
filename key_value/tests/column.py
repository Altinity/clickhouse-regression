from key_value.tests.steps import *


@TestScenario
def column_input(self, node=None):
    """Check that clickhouse extractKeyValuePairs function support column input."""

    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    with Given("I have a table"):
        create_partitioned_table(table_name=table_name, extra_table_col=",y String")

    input_strings = ["""''""",
                     """'9 ads =nm,  no\:me: neymar, age: 30, daojmskdpoa and a  height:   1.75, school: lupe\ picasso, team: psg,'""",
                     """'2582511992885811767 Qfic:QELUWB, BciBbb:9, IeyClzKmrs {Pvkrq:86093, Glhbmwg:5, FtuzyjOsf:66, YssMbiUswk:0, AxuDcgzkpx:1, KacsIbu:277, MgmjkhKh:9q60pqp43s246u2745, KucFjl:61350852, SdfbJshj:5462619308589345326}, UzfFmg {IsaRubn:3, PqgPmah:954, JagRddm:31692}, KnxKigysBjo {Mnfmybl:7941, Vnvpht:xghk, BgqvTj:9843, UlnrrCr:72940085719217638, YawhzZkqv:260753, QyxbSqamh:627.4022, Ulejhjgk:-0, DjyecbleCqazeZdyc:2229740235971220001, YocxsggkXvxwWzgd:2320663994026035210, NhntkbcQzghj:6}, Rdodi {OSERVWEI_MIVZAPPDLCR_JT:"068G14THM", KFQMUR_HXEVFA:"XZSQ", DVCRIJ_ZOUMQ_DD:"P0889542750958729205", XNFHGSSF_RHRUZHVBS_KWBT:"F", DIOQZO_PVNNTGISHEH_VB:"bmhncvchhrepqnxb", BHMYYKME_VCPWN_QR:754501869725462264, SYZIWCHJK:2z1791877467804982}, Zfv {AyvbOrexdlUdzj:"GESF", FescvXwmfFlgijw:"RPUGI|RULHKBESCT", RvnzbdkCwjt:"3087"}, UetXuhy {R_YU_FVBD_TCGUTEDZU_BBVAK:0422461531412992163, G_OV_WBLZ_WMMJKMHQZ:5216958198816473961, B_REU_XUQXBYR_LVOIMULK_MMSN:IcmniychTgxn{unsaurbrLnaqQc:1, fbqiUtcjYul:20911}}, AuorsGvyImnh {P_EWJN:"JFVL"}'""",
                     """'123ab:123ab'"""
                     ]
    output_strings = ["""{}""",
                      """{'no:me':'neymar','age':'30','height':'1.75','school':'lupe picasso','team':'psg'}""",
                      """{'Qfic':'QELUWB','Mnfmybl':'7941','SYZIWCHJK':'2z1791877467804982','Pvkrq':'86093','R_YU_FVBD_TCGUTEDZU_BBVAK':'0422461531412992163','DjyecbleCqazeZdyc':'2229740235971220001','KacsIbu':'277','Vnvpht':'xghk','BciBbb':'9','B_REU_XUQXBYR_LVOIMULK_MMSN':'IcmniychTgxn','JagRddm':'31692','Glhbmwg':'5','MgmjkhKh':'9q60pqp43s246u2745','YawhzZkqv':'260753','P_EWJN':'JFVL','QyxbSqamh':'627.4022','SdfbJshj':'5462619308589345326','unsaurbrLnaqQc':'1','YssMbiUswk':'0','KucFjl':'61350852','FtuzyjOsf':'66','BHMYYKME_VCPWN_QR':'754501869725462264','PqgPmah':'954','RvnzbdkCwjt':'3087','BgqvTj':'9843','UlnrrCr':'72940085719217638','IsaRubn':'3','FescvXwmfFlgijw':'RPUGI|RULHKBESCT','Ulejhjgk':'0','DVCRIJ_ZOUMQ_DD':'P0889542750958729205','AyvbOrexdlUdzj':'GESF','YocxsggkXvxwWzgd':'2320663994026035210','AxuDcgzkpx':'1','NhntkbcQzghj':'6','OSERVWEI_MIVZAPPDLCR_JT':'068G14THM','KFQMUR_HXEVFA':'XZSQ','XNFHGSSF_RHRUZHVBS_KWBT':'F','DIOQZO_PVNNTGISHEH_VB':'bmhncvchhrepqnxb','G_OV_WBLZ_WMMJKMHQZ':'5216958198816473961','fbqiUtcjYul':'20911'}""",
                      """{'ab':'123ab'}"""
                      ]
    with When("I insert values into the table"):
        for i, input_string in enumerate(input_strings):
            output_string = output_strings[i]
            insert(table_name=table_name, x=input_string, y=output_string.replace("'", "\\'"))

    with Then("I check extractKeyValuePairs function returns correct value"):
        r = node.query(f"""select min(toString(extractKeyValuePairs(x, '\\\\\\\\', ':', ',', '\\"', '.')) == y) from {table_name}""", pipe_cmd="echo")
        assert r.output == '1', error()


@TestModule
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parsing_RecognizedKeyValuePairs("1.0"),
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Key_Format("1.0"),
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Value_Format("1.0"),
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Format_Input("1.0"),
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Format_Output("1.0")
)
@Name("column")
def feature(self, node="clickhouse1"):
    """Check that clickhouse extractKeyValuePairs function support column input."""

    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
