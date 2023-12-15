# SRS-031 ClickHouse Aggregate Functions
# Software Requirements Specification

## Table of Contents

* 1 [Revision History](#revision-history)
* 2 [Introduction](#introduction)
* 3 [Requirements](#requirements)
    * 3.1 [Aggregate Functions](#aggregate-functions)
        * 3.1.1 [Standard Functions](#standard-functions)
            * 3.1.1.1 [count](#count)
                * 3.1.1.1.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count](#rqsrs-031clickhouseaggregatefunctionsstandardcount)
                * 3.1.1.1.2 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count.DistinctImplementationSetting](#rqsrs-031clickhouseaggregatefunctionsstandardcountdistinctimplementationsetting)
                * 3.1.1.1.3 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count.OptimizeTrivialCountQuerySetting](#rqsrs-031clickhouseaggregatefunctionsstandardcountoptimizetrivialcountquerysetting)
                * 3.1.1.1.4 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count.OptimizeFunctionsToSubcolumnsSetting](#rqsrs-031clickhouseaggregatefunctionsstandardcountoptimizefunctionstosubcolumnssetting)
            * 3.1.1.2 [min](#min)
                * 3.1.1.2.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Min](#rqsrs-031clickhouseaggregatefunctionsstandardmin)
            * 3.1.1.3 [max](#max)
                * 3.1.1.3.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Max](#rqsrs-031clickhouseaggregatefunctionsstandardmax)
            * 3.1.1.4 [sum](#sum)
                * 3.1.1.4.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Sum](#rqsrs-031clickhouseaggregatefunctionsstandardsum)
            * 3.1.1.5 [avg](#avg)
                * 3.1.1.5.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Avg](#rqsrs-031clickhouseaggregatefunctionsstandardavg)
            * 3.1.1.6 [any](#any)
                * 3.1.1.6.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Any](#rqsrs-031clickhouseaggregatefunctionsstandardany)
            * 3.1.1.7 [stddevPop](#stddevpop)
                * 3.1.1.7.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.StddevPop](#rqsrs-031clickhouseaggregatefunctionsstandardstddevpop)
            * 3.1.1.8 [stddevSamp](#stddevsamp)
                * 3.1.1.8.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.StddevSamp](#rqsrs-031clickhouseaggregatefunctionsstandardstddevsamp)
            * 3.1.1.9 [varPop](#varpop)
                * 3.1.1.9.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.VarPop](#rqsrs-031clickhouseaggregatefunctionsstandardvarpop)
            * 3.1.1.10 [varSamp](#varsamp)
                * 3.1.1.10.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.VarSamp](#rqsrs-031clickhouseaggregatefunctionsstandardvarsamp)
            * 3.1.1.11 [covarPop](#covarpop)
                * 3.1.1.11.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.CovarPop](#rqsrs-031clickhouseaggregatefunctionsstandardcovarpop)
            * 3.1.1.12 [covarSamp](#covarsamp)
                * 3.1.1.12.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.CovarSamp](#rqsrs-031clickhouseaggregatefunctionsstandardcovarsamp)
        * 3.1.2 [Specific Functions](#specific-functions)
            * 3.1.2.1 [anyHeavy](#anyheavy)
                * 3.1.2.1.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.AnyHeavy](#rqsrs-031clickhouseaggregatefunctionsspecificanyheavy)
            * 3.1.2.2 [anyLast](#anylast)
                * 3.1.2.2.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.AnyLast](#rqsrs-031clickhouseaggregatefunctionsspecificanylast)
            * 3.1.2.3 [argMin](#argmin)
                * 3.1.2.3.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.ArgMin](#rqsrs-031clickhouseaggregatefunctionsspecificargmin)
            * 3.1.2.4 [argMax](#argmax)
                * 3.1.2.4.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.ArgMax](#rqsrs-031clickhouseaggregatefunctionsspecificargmax)
            * 3.1.2.5 [avgWeighted](#avgweighted)
                * 3.1.2.5.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.AvgWeighted](#rqsrs-031clickhouseaggregatefunctionsspecificavgweighted)
            * 3.1.2.6 [topK](#topk)
                * 3.1.2.6.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.TopK](#rqsrs-031clickhouseaggregatefunctionsspecifictopk)
            * 3.1.2.7 [topKWeighted](#topkweighted)
                * 3.1.2.7.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.TopKWeighted](#rqsrs-031clickhouseaggregatefunctionsspecifictopkweighted)
            * 3.1.2.8 [groupArray](#grouparray)
                * 3.1.2.8.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArray](#rqsrs-031clickhouseaggregatefunctionsspecificgrouparray)
            * 3.1.2.9 [groupArrayLast](#grouparraylast)
                * 3.1.2.9.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayLast](#rqsrs-031clickhouseaggregatefunctionsspecificgrouparraylast)
            * 3.1.2.10 [groupUniqArray](#groupuniqarray)
                * 3.1.2.10.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupUniqArray](#rqsrs-031clickhouseaggregatefunctionsspecificgroupuniqarray)
            * 3.1.2.11 [groupArrayInsertAt](#grouparrayinsertat)
                * 3.1.2.11.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayInsertAt](#rqsrs-031clickhouseaggregatefunctionsspecificgrouparrayinsertat)
            * 3.1.2.12 [groupArrayMovingAvg](#grouparraymovingavg)
                * 3.1.2.12.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayMovingAvg](#rqsrs-031clickhouseaggregatefunctionsspecificgrouparraymovingavg)
            * 3.1.2.13 [groupArrayMovingSum](#grouparraymovingsum)
                * 3.1.2.13.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayMovingSum](#rqsrs-031clickhouseaggregatefunctionsspecificgrouparraymovingsum)
            * 3.1.2.14 [groupArraySample](#grouparraysample)
                * 3.1.2.14.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArraySample](#rqsrs-031clickhouseaggregatefunctionsspecificgrouparraysample)
            * 3.1.2.15 [groupBitAnd](#groupbitand)
                * 3.1.2.15.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitAnd](#rqsrs-031clickhouseaggregatefunctionsspecificgroupbitand)
            * 3.1.2.16 [groupBitOr](#groupbitor)
                * 3.1.2.16.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitOr](#rqsrs-031clickhouseaggregatefunctionsspecificgroupbitor)
            * 3.1.2.17 [groupBitXor](#groupbitxor)
                * 3.1.2.17.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitXor](#rqsrs-031clickhouseaggregatefunctionsspecificgroupbitxor)
            * 3.1.2.18 [groupBitmap](#groupbitmap)
                * 3.1.2.18.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmap](#rqsrs-031clickhouseaggregatefunctionsspecificgroupbitmap)
            * 3.1.2.19 [groupBitmapAnd](#groupbitmapand)
                * 3.1.2.19.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmapAnd](#rqsrs-031clickhouseaggregatefunctionsspecificgroupbitmapand)
            * 3.1.2.20 [groupBitmapOr](#groupbitmapor)
                * 3.1.2.20.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmapOr](#rqsrs-031clickhouseaggregatefunctionsspecificgroupbitmapor)
            * 3.1.2.21 [groupBitmapXor](#groupbitmapxor)
                * 3.1.2.21.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmapXor](#rqsrs-031clickhouseaggregatefunctionsspecificgroupbitmapxor)
            * 3.1.2.22 [sumWithOverflow](#sumwithoverflow)
                * 3.1.2.22.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumWithOverflow](#rqsrs-031clickhouseaggregatefunctionsspecificsumwithoverflow)
            * 3.1.2.23 [sumMap](#summap)
                * 3.1.2.23.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumMap](#rqsrs-031clickhouseaggregatefunctionsspecificsummap)
            * 3.1.2.24 [minMap](#minmap)
                * 3.1.2.24.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MinMap](#rqsrs-031clickhouseaggregatefunctionsspecificminmap)
            * 3.1.2.25 [maxMap](#maxmap)
                * 3.1.2.25.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MaxMap](#rqsrs-031clickhouseaggregatefunctionsspecificmaxmap)
            * 3.1.2.26 [skewSamp](#skewsamp)
                * 3.1.2.26.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SkewSamp](#rqsrs-031clickhouseaggregatefunctionsspecificskewsamp)
            * 3.1.2.27 [skewPop](#skewpop)
                * 3.1.2.27.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SkewPop](#rqsrs-031clickhouseaggregatefunctionsspecificskewpop)
            * 3.1.2.28 [kurtSamp](#kurtsamp)
                * 3.1.2.28.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.KurtSamp](#rqsrs-031clickhouseaggregatefunctionsspecifickurtsamp)
            * 3.1.2.29 [kurtPop](#kurtpop)
                * 3.1.2.29.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.KurtPop](#rqsrs-031clickhouseaggregatefunctionsspecifickurtpop)
            * 3.1.2.30 [uniq](#uniq)
                * 3.1.2.30.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Uniq](#rqsrs-031clickhouseaggregatefunctionsspecificuniq)
            * 3.1.2.31 [uniqExact](#uniqexact)
                * 3.1.2.31.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqExact](#rqsrs-031clickhouseaggregatefunctionsspecificuniqexact)
            * 3.1.2.32 [uniqCombined](#uniqcombined)
                * 3.1.2.32.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqCombined](#rqsrs-031clickhouseaggregatefunctionsspecificuniqcombined)
            * 3.1.2.33 [uniqCombined64](#uniqcombined64)
                * 3.1.2.33.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqCombined64](#rqsrs-031clickhouseaggregatefunctionsspecificuniqcombined64)
            * 3.1.2.34 [uniqHLL12](#uniqhll12)
                * 3.1.2.34.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqHLL12](#rqsrs-031clickhouseaggregatefunctionsspecificuniqhll12)
            * 3.1.2.35 [quantile](#quantile)
                * 3.1.2.35.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Quantile](#rqsrs-031clickhouseaggregatefunctionsspecificquantile)
            * 3.1.2.36 [quantiles](#quantiles)
                * 3.1.2.36.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Quantiles](#rqsrs-031clickhouseaggregatefunctionsspecificquantiles)
            * 3.1.2.37 [quantilesExactExclusive](#quantilesexactexclusive)
                * 3.1.2.37.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactExclusive](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesexactexclusive)
            * 3.1.2.38 [quantilesExactInclusive](#quantilesexactinclusive)
                * 3.1.2.38.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactInclusive](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesexactinclusive)
            * 3.1.2.39 [quantilesDeterministic](#quantilesdeterministic)
                * 3.1.2.39.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesDeterministic](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesdeterministic)
            * 3.1.2.40 [quantilesExact](#quantilesexact)
                * 3.1.2.40.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExact](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesexact)
            * 3.1.2.41 [quantilesExactHigh](#quantilesexacthigh)
                * 3.1.2.41.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactHigh](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesexacthigh)
            * 3.1.2.42 [quantilesExactLow](#quantilesexactlow)
                * 3.1.2.42.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactLow](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesexactlow)
            * 3.1.2.43 [quantilesExactWeighted](#quantilesexactweighted)
                * 3.1.2.43.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactWeighted](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesexactweighted)
            * 3.1.2.44 [quantilesTDigest](#quantilestdigest)
                * 3.1.2.44.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTDigest](#rqsrs-031clickhouseaggregatefunctionsspecificquantilestdigest)
            * 3.1.2.45 [quantilesTDigestWeighted](#quantilestdigestweighted)
                * 3.1.2.45.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTDigestWeighted](#rqsrs-031clickhouseaggregatefunctionsspecificquantilestdigestweighted)
            * 3.1.2.46 [quantilesBFloat16](#quantilesbfloat16)
                * 3.1.2.46.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesBFloat16](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesbfloat16)
            * 3.1.2.47 [quantilesBFloat16Weighted](#quantilesbfloat16weighted)
                * 3.1.2.47.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesBFloat16Weighted](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesbfloat16weighted)
            * 3.1.2.48 [quantilesTiming](#quantilestiming)
                * 3.1.2.48.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTiming](#rqsrs-031clickhouseaggregatefunctionsspecificquantilestiming)
            * 3.1.2.49 [quantilesTimingWeighted](#quantilestimingweighted)
                * 3.1.2.49.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTimingWeighted](#rqsrs-031clickhouseaggregatefunctionsspecificquantilestimingweighted)
            * 3.1.2.50 [quantilesGK](#quantilesgk)
                * 3.1.2.50.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesGK](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesgk)
            * 3.1.2.51 [quantilesInterpolatedWeighted](#quantilesinterpolatedweighted)
                * 3.1.2.51.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesInterpolatedWeighted](#rqsrs-031clickhouseaggregatefunctionsspecificquantilesinterpolatedweighted)
            * 3.1.2.52 [quantileExact](#quantileexact)
                * 3.1.2.52.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExact](#rqsrs-031clickhouseaggregatefunctionsspecificquantileexact)
            * 3.1.2.53 [quantileExactLow](#quantileexactlow)
                * 3.1.2.53.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExactLow](#rqsrs-031clickhouseaggregatefunctionsspecificquantileexactlow)
            * 3.1.2.54 [quantileExactHigh](#quantileexacthigh)
                * 3.1.2.54.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExactHigh](#rqsrs-031clickhouseaggregatefunctionsspecificquantileexacthigh)
            * 3.1.2.55 [quantileExactWeighted](#quantileexactweighted)
                * 3.1.2.55.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExactWeighted](#rqsrs-031clickhouseaggregatefunctionsspecificquantileexactweighted)
            * 3.1.2.56 [quantileTiming](#quantiletiming)
                * 3.1.2.56.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTiming](#rqsrs-031clickhouseaggregatefunctionsspecificquantiletiming)
            * 3.1.2.57 [quantileTimingWeighted](#quantiletimingweighted)
                * 3.1.2.57.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTimingWeighted](#rqsrs-031clickhouseaggregatefunctionsspecificquantiletimingweighted)
            * 3.1.2.58 [quantileDeterministic](#quantiledeterministic)
                * 3.1.2.58.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileDeterministic](#rqsrs-031clickhouseaggregatefunctionsspecificquantiledeterministic)
            * 3.1.2.59 [quantileTDigest](#quantiletdigest)
                * 3.1.2.59.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTDigest](#rqsrs-031clickhouseaggregatefunctionsspecificquantiletdigest)
            * 3.1.2.60 [quantileTDigestWeighted](#quantiletdigestweighted)
                * 3.1.2.60.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTDigestWeighted](#rqsrs-031clickhouseaggregatefunctionsspecificquantiletdigestweighted)
            * 3.1.2.61 [quantileBFloat16](#quantilebfloat16)
                * 3.1.2.61.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileBFloat16](#rqsrs-031clickhouseaggregatefunctionsspecificquantilebfloat16)
            * 3.1.2.62 [quantileBFloat16Weighted](#quantilebfloat16weighted)
                * 3.1.2.62.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileBFloat16Weighted](#rqsrs-031clickhouseaggregatefunctionsspecificquantilebfloat16weighted)
            * 3.1.2.63 [quantileInterpolatedWeighted](#quantileinterpolatedweighted)
                * 3.1.2.63.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileInterpolatedWeighted](#rqsrs-031clickhouseaggregatefunctionsspecificquantileinterpolatedweighted)
            * 3.1.2.64 [quantileGK](#quantilegk)
                * 3.1.2.64.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileGK](#rqsrs-031clickhouseaggregatefunctionsspecificquantilegk)
            * 3.1.2.65 [simpleLinearRegression](#simplelinearregression)
                * 3.1.2.65.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SimpleLinearRegression](#rqsrs-031clickhouseaggregatefunctionsspecificsimplelinearregression)
            * 3.1.2.66 [stochasticLinearRegression](#stochasticlinearregression)
                * 3.1.2.66.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.StochasticLinearRegression](#rqsrs-031clickhouseaggregatefunctionsspecificstochasticlinearregression)
            * 3.1.2.67 [stochasticLogisticRegression](#stochasticlogisticregression)
                * 3.1.2.67.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.StochasticLogisticRegression](#rqsrs-031clickhouseaggregatefunctionsspecificstochasticlogisticregression)
            * 3.1.2.68 [categoricalInformationValue](#categoricalinformationvalue)
                * 3.1.2.68.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.CategoricalInformationValue](#rqsrs-031clickhouseaggregatefunctionsspecificcategoricalinformationvalue)
            * 3.1.2.69 [studentTTest](#studentttest)
                * 3.1.2.69.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.StudentTTest](#rqsrs-031clickhouseaggregatefunctionsspecificstudentttest)
            * 3.1.2.70 [welchTTest](#welchttest)
                * 3.1.2.70.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.WelchTTest](#rqsrs-031clickhouseaggregatefunctionsspecificwelchttest)
            * 3.1.2.71 [mannWhitneyUTest](#mannwhitneyutest)
                * 3.1.2.71.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MannWhitneyUTest](#rqsrs-031clickhouseaggregatefunctionsspecificmannwhitneyutest)
            * 3.1.2.72 [median](#median)
                * 3.1.2.72.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Median](#rqsrs-031clickhouseaggregatefunctionsspecificmedian)
            * 3.1.2.73 [rankCorr](#rankcorr)
                * 3.1.2.73.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.RankCorr](#rqsrs-031clickhouseaggregatefunctionsspecificrankcorr)
            * 3.1.2.74 [entropy](#entropy)
                * 3.1.2.74.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Entropy](#rqsrs-031clickhouseaggregatefunctionsspecificentropy)
            * 3.1.2.75 [meanZTest](#meanztest)
                * 3.1.2.75.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MeanZTest](#rqsrs-031clickhouseaggregatefunctionsspecificmeanztest)
            * 3.1.2.76 [sparkbar](#sparkbar)
                * 3.1.2.76.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Sparkbar](#rqsrs-031clickhouseaggregatefunctionsspecificsparkbar)
            * 3.1.2.77 [corr](#corr)
                * 3.1.2.77.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Corr](#rqsrs-031clickhouseaggregatefunctionsspecificcorr)
            * 3.1.2.78 [deltaSum](#deltasum)
                * 3.1.2.78.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.DeltaSum](#rqsrs-031clickhouseaggregatefunctionsspecificdeltasum)
            * 3.1.2.79 [deltaSumTimestamp](#deltasumtimestamp)
                * 3.1.2.79.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.DeltaSumTimestamp](#rqsrs-031clickhouseaggregatefunctionsspecificdeltasumtimestamp)
            * 3.1.2.80 [exponentialMovingAverage](#exponentialmovingaverage)
                * 3.1.2.80.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.ExponentialMovingAverage](#rqsrs-031clickhouseaggregatefunctionsspecificexponentialmovingaverage)
            * 3.1.2.81 [intervalLengthSum](#intervallengthsum)
                * 3.1.2.81.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.IntervalLengthSum](#rqsrs-031clickhouseaggregatefunctionsspecificintervallengthsum)
        * 3.1.3 [kolmogorovSmirnovTest](#kolmogorovsmirnovtest)
                * 3.1.3.81.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.KolmogorovSmirnovTest](#rqsrs-031clickhouseaggregatefunctionsspecifickolmogorovsmirnovtest)
            * 3.1.3.82 [sumCount](#sumcount)
                * 3.1.3.82.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumCount](#rqsrs-031clickhouseaggregatefunctionsspecificsumcount)
            * 3.1.3.83 [sumKahan](#sumkahan)
                * 3.1.3.83.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumKahan](#rqsrs-031clickhouseaggregatefunctionsspecificsumkahan)
            * 3.1.3.84 [corrMatrix](#corrmatrix)
                * 3.1.3.84.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.CorrMatrix](#rqsrs-031clickhouseaggregatefunctionsspecificcorrmatrix)
            * 3.1.3.85 [covarSampMatrix](#covarsampmatrix)
                * 3.1.3.85.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.CovarSampMatrix](#rqsrs-031clickhouseaggregatefunctionsspecificcovarsampmatrix)
            * 3.1.3.86 [covarPopMatrix](#covarpopmatrix)
                * 3.1.3.86.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.CovarPopMatrix](#rqsrs-031clickhouseaggregatefunctionsspecificcovarpopmatrix)
        * 3.1.4 [Miscellaneous Functions](#miscellaneous-functions)
            * 3.1.4.1 [first_value](#first_value)
                * 3.1.4.1.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.FirstValue](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousfirstvalue)
            * 3.1.4.2 [first_value_respect_nulls](#first_value_respect_nulls)
                * 3.1.4.2.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.FirstValueRespectNulls](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousfirstvaluerespectnulls)
            * 3.1.4.3 [last_value](#last_value)
                * 3.1.4.3.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LastValue](#rqsrs-031clickhouseaggregatefunctionsmiscellaneouslastvalue)
            * 3.1.4.4 [last_value_respect_nulls](#last_value_respect_nulls)
                * 3.1.4.4.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LastValueRespectNulls](#rqsrs-031clickhouseaggregatefunctionsmiscellaneouslastvaluerespectnulls)
            * 3.1.4.5 [lagInFrame](#laginframe)
                * 3.1.4.5.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LagInFrame](#rqsrs-031clickhouseaggregatefunctionsmiscellaneouslaginframe)
            * 3.1.4.6 [leadInFrame](#leadinframe)
                * 3.1.4.6.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LeadInFrame](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousleadinframe)
            * 3.1.4.7 [nth_value](#nth_value)
                * 3.1.4.7.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.NthValue](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousnthvalue)
            * 3.1.4.8 [rank](#rank)
                * 3.1.4.8.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Rank](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousrank)
            * 3.1.4.9 [row_number](#row_number)
                * 3.1.4.9.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.RowNumber](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousrownumber)
            * 3.1.4.10 [ntile](#ntile)
                * 3.1.4.10.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Ntile](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousntile)
            * 3.1.4.11 [singleValueOrNull](#singlevalueornull)
                * 3.1.4.11.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SingleValueOrNull](#rqsrs-031clickhouseaggregatefunctionsmiscellaneoussinglevalueornull)
            * 3.1.4.12 [maxIntersections](#maxintersections)
                * 3.1.4.12.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MaxIntersections](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousmaxintersections)
            * 3.1.4.13 [maxIntersectionsPosition](#maxintersectionsposition)
                * 3.1.4.13.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MaxIntersectionsPosition](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousmaxintersectionsposition)
            * 3.1.4.14 [aggThrow](#aggthrow)
                * 3.1.4.14.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.AggThrow](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousaggthrow)
            * 3.1.4.15 [boundingRatio](#boundingratio)
                * 3.1.4.15.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.BoundingRatio](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousboundingratio)
            * 3.1.4.16 [contingency](#contingency)
                * 3.1.4.16.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Contingency](#rqsrs-031clickhouseaggregatefunctionsmiscellaneouscontingency)
            * 3.1.4.17 [cramersV](#cramersv)
                * 3.1.4.17.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.CramersV](#rqsrs-031clickhouseaggregatefunctionsmiscellaneouscramersv)
            * 3.1.4.18 [cramersVBiasCorrected](#cramersvbiascorrected)
                * 3.1.4.18.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.CramersVBiasCorrected](#rqsrs-031clickhouseaggregatefunctionsmiscellaneouscramersvbiascorrected)
            * 3.1.4.19 [dense_rank](#dense_rank)
                * 3.1.4.19.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.DenseRank](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousdenserank)
            * 3.1.4.20 [exponentialTimeDecayedAvg](#exponentialtimedecayedavg)
                * 3.1.4.20.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedAvg](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousexponentialtimedecayedavg)
            * 3.1.4.21 [exponentialTimeDecayedCount](#exponentialtimedecayedcount)
                * 3.1.4.21.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedCount](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousexponentialtimedecayedcount)
            * 3.1.4.22 [exponentialTimeDecayedMax](#exponentialtimedecayedmax)
                * 3.1.4.22.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedMax](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousexponentialtimedecayedmax)
            * 3.1.4.23 [exponentialTimeDecayedSum](#exponentialtimedecayedsum)
                * 3.1.4.23.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedSum](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousexponentialtimedecayedsum)
            * 3.1.4.24 [uniqTheta](#uniqtheta)
                * 3.1.4.24.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.UniqTheta](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousuniqtheta)
            * 3.1.4.25 [quantileExactExclusive](#quantileexactexclusive)
                * 3.1.4.25.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.QuantileExactExclusive](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousquantileexactexclusive)
            * 3.1.4.26 [quantileExactInclusive](#quantileexactinclusive)
                * 3.1.4.26.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.QuantileExactInclusive](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousquantileexactinclusive)
            * 3.1.4.27 [sumMapFilteredWithOverflow](#summapfilteredwithoverflow)
                * 3.1.4.27.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SumMapFilteredWithOverflow](#rqsrs-031clickhouseaggregatefunctionsmiscellaneoussummapfilteredwithoverflow)
            * 3.1.4.28 [sumMapWithOverflow](#summapwithoverflow)
                * 3.1.4.28.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SumMapWithOverflow](#rqsrs-031clickhouseaggregatefunctionsmiscellaneoussummapwithoverflow)
            * 3.1.4.29 [sumMappedArrays](#summappedarrays)
                * 3.1.4.29.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SumMappedArrays](#rqsrs-031clickhouseaggregatefunctionsmiscellaneoussummappedarrays)
            * 3.1.4.30 [nothing](#nothing)
                * 3.1.4.30.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Nothing](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousnothing)
            * 3.1.4.31 [maxMappedArrays](#maxmappedarrays)
                * 3.1.4.31.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MaxMappedArrays](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousmaxmappedarrays)
            * 3.1.4.32 [minMappedArrays](#minmappedarrays)
                * 3.1.4.32.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MinMappedArrays](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousminmappedarrays)
            * 3.1.4.33 [nonNegativeDerivative](#nonnegativederivative)
                * 3.1.4.33.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.NonNegativeDerivative](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousnonnegativederivative)
            * 3.1.4.34 [theilsU](#theilsu)
                * 3.1.4.34.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.TheilsU](#rqsrs-031clickhouseaggregatefunctionsmiscellaneoustheilsu)
            * 3.1.4.35 [analysisOfVariance](#analysisofvariance)
                * 3.1.4.35.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.AnalysisOfVariance](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousanalysisofvariance)
            * 3.1.4.36 [flameGraph](#flamegraph)
                * 3.1.4.36.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.FlameGraph](#rqsrs-031clickhouseaggregatefunctionsmiscellaneousflamegraph)
        * 3.1.5 [Parametric Functions](#parametric-functions)
            * 3.1.5.1 [histogram](#histogram)
                * 3.1.5.1.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.Histogram](#rqsrs-031clickhouseaggregatefunctionsparametrichistogram)
            * 3.1.5.2 [sequenceMatch](#sequencematch)
                * 3.1.5.2.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SequenceMatch](#rqsrs-031clickhouseaggregatefunctionsparametricsequencematch)
            * 3.1.5.3 [sequenceCount](#sequencecount)
                * 3.1.5.3.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SequenceCount](#rqsrs-031clickhouseaggregatefunctionsparametricsequencecount)
            * 3.1.5.4 [windowFunnel](#windowfunnel)
                * 3.1.5.4.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.WindowFunnel](#rqsrs-031clickhouseaggregatefunctionsparametricwindowfunnel)
            * 3.1.5.5 [retention](#retention)
                * 3.1.5.5.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.Retention](#rqsrs-031clickhouseaggregatefunctionsparametricretention)
            * 3.1.5.6 [uniqUpTo](#uniqupto)
                * 3.1.5.6.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.UniqUpTo](#rqsrs-031clickhouseaggregatefunctionsparametricuniqupto)
            * 3.1.5.7 [sumMapFiltered](#summapfiltered)
                * 3.1.5.7.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SumMapFiltered](#rqsrs-031clickhouseaggregatefunctionsparametricsummapfiltered)
            * 3.1.5.8 [sequenceNextNode](#sequencenextnode)
                * 3.1.5.8.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SequenceNextNode](#rqsrs-031clickhouseaggregatefunctionsparametricsequencenextnode)
            * 3.1.5.9 [largestTriangleThreeBuckets](#largesttrianglethreebuckets)
                * 3.1.5.9.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.LargestTriangleThreeBuckets](#rqsrs-031clickhouseaggregatefunctionsparametriclargesttrianglethreebuckets)
    * 3.2 [Combinator Functions](#combinator-functions)
        * 3.2.1 [-If Suffix](#-if-suffix)
            * 3.2.1.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.If](#rqsrs-031clickhouseaggregatefunctionscombinatorif)
        * 3.2.2 [-Array Suffix](#-array-suffix)
            * 3.2.2.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Array](#rqsrs-031clickhouseaggregatefunctionscombinatorarray)
        * 3.2.3 [-Map Suffix](#-map-suffix)
            * 3.2.3.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Map](#rqsrs-031clickhouseaggregatefunctionscombinatormap)
        * 3.2.4 [-State Suffix](#-state-suffix)
            * 3.2.4.1 [Test Feature Diagram](#test-feature-diagram)
            * 3.2.4.2 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State](#rqsrs-031clickhouseaggregatefunctionscombinatorstate)
            * 3.2.4.3 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.AggregatingMergeTree](#rqsrs-031clickhouseaggregatefunctionscombinatorstatewithaggregatingmergetree)
            * 3.2.4.4 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.InitializeAggregationFunction](#rqsrs-031clickhouseaggregatefunctionscombinatorstatewithinitializeaggregationfunction)
            * 3.2.4.5 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.FinalizeAggregationFunction](#rqsrs-031clickhouseaggregatefunctionscombinatorstatewithfinalizeaggregationfunction)
            * 3.2.4.6 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.RunningAccumulateFunction](#rqsrs-031clickhouseaggregatefunctionscombinatorstatewithrunningaccumulatefunction)
            * 3.2.4.7 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.Merge](#rqsrs-031clickhouseaggregatefunctionscombinatorstatewithmerge)
            * 3.2.4.8 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.MergeState](#rqsrs-031clickhouseaggregatefunctionscombinatorstatewithmergestate)
            * 3.2.4.9 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.AggregateFunctionDataType](#rqsrs-031clickhouseaggregatefunctionscombinatorstatewithaggregatefunctiondatatype)
            * 3.2.4.10 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.MaterializedView](#rqsrs-031clickhouseaggregatefunctionscombinatorstatewithmaterializedview)
        * 3.2.5 [-SimpleState Suffix](#-simplestate-suffix)
            * 3.2.5.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.SimpleState](#rqsrs-031clickhouseaggregatefunctionscombinatorsimplestate)
            * 3.2.5.2 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.SimpleState.With.AggregatingMergeTree](#rqsrs-031clickhouseaggregatefunctionscombinatorsimplestatewithaggregatingmergetree)
        * 3.2.6 [-Merge Suffix](#-merge-suffix)
            * 3.2.6.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Merge](#rqsrs-031clickhouseaggregatefunctionscombinatormerge)
        * 3.2.7 [-MergeState Suffix](#-mergestate-suffix)
            * 3.2.7.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.MergeState](#rqsrs-031clickhouseaggregatefunctionscombinatormergestate)
        * 3.2.8 [-ForEach Suffix](#-foreach-suffix)
            * 3.2.8.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.ForEach](#rqsrs-031clickhouseaggregatefunctionscombinatorforeach)
        * 3.2.9 [-Distinct Suffix](#-distinct-suffix)
            * 3.2.9.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Distinct](#rqsrs-031clickhouseaggregatefunctionscombinatordistinct)
        * 3.2.10 [-OrDefault Suffix](#-ordefault-suffix)
            * 3.2.10.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.OrDefault](#rqsrs-031clickhouseaggregatefunctionscombinatorordefault)
        * 3.2.11 [-OrNull Suffix](#-ornull-suffix)
            * 3.2.11.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.OrNull](#rqsrs-031clickhouseaggregatefunctionscombinatorornull)
        * 3.2.12 [-Resample Suffix](#-resample-suffix)
            * 3.2.12.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Resample](#rqsrs-031clickhouseaggregatefunctionscombinatorresample)
        * 3.2.13 [--ArgMin Suffix](#--argmin-suffix)
            * 3.2.13.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.ArgMin](#rqsrs-031clickhouseaggregatefunctionscombinatorargmin)
        * 3.2.14 [--ArgMax Suffix](#--argmax-suffix)
            * 3.2.14.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.ArgMax](#rqsrs-031clickhouseaggregatefunctionscombinatorargmax)
    * 3.3 [Data Types](#data-types)
        * 3.3.1 [SimpleAggregateFunction](#simpleaggregatefunction)
            * 3.3.1.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.SimpleAggregateFunction](#rqsrs-031clickhouseaggregatefunctionsdatatypesimpleaggregatefunction)
        * 3.3.2 [AggregateFunction](#aggregatefunction)
            * 3.3.2.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.AggregateFunction](#rqsrs-031clickhouseaggregatefunctionsdatatypeaggregatefunction)
            * 3.3.2.2 [Inserting Data](#inserting-data)
                * 3.3.2.2.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.AggregateFunction.Insert](#rqsrs-031clickhouseaggregatefunctionsdatatypeaggregatefunctioninsert)
            * 3.3.2.3 [Selecting Data](#selecting-data)
                * 3.3.2.3.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.AggregateFunction.Select](#rqsrs-031clickhouseaggregatefunctionsdatatypeaggregatefunctionselect)
    * 3.4 [Grouping](#grouping)
        * 3.4.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.Grouping](#rqsrs-031clickhouseaggregatefunctionsgrouping)
    * 3.5 [Grouping Sets](#grouping-sets)
        * 3.5.1 [RQ.SRS-031.ClickHouse.AggregateFunctions.GroupingSets](#rqsrs-031clickhouseaggregatefunctionsgroupingsets)
* 4 [References](#references)

## Revision History

This document is stored in an electronic form using [Git] source control management software
hosted in a [GitHub Repository].
All the updates are tracked using the [Revision History].

## Introduction

This software requirements specification covers requirements for [aggregate function]s and corresponding
data types in [ClickHouse].

## Requirements

### Aggregate Functions

#### Standard Functions

##### count

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count
version: 1.0

[ClickHouse] SHALL support [count] standard aggregate function.

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count.DistinctImplementationSetting
version: 1.0

[ClickHouse] SHALL support [count_distinct_implementation](https://clickhouse.com/docs/en/operations/settings/settings#settings-count_distinct_implementation) setting that SHALL specify
which `uniq*` function SHALL be used to calculate `COUNT(DISTINCT expr)`. 

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count.OptimizeTrivialCountQuerySetting
version: 1.0

[ClickHouse] SHALL support [optimize_trivial_count_query]https://clickhouse.com/docs/en/operations/settings/settings#optimize-trivial-count-query setting that SHALL enable or disable
the optimization of trivial `SELECT count() FROM table` query using metadata from [MergeTree] tables.


###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Count.OptimizeFunctionsToSubcolumnsSetting
version: 1.0

[ClickHouse] SHALL support optimizing `SELECT count(nullable_column) FROM table` query by enabling the
[optimize_functions_to_subcolumns](https://clickhouse.com/docs/en/operations/settings/settings#optimize-functions-to-subcolumns) setting. With `optimize_functions_to_subcolumns=1` the function SHALL
read only null sub-column instead of reading and processing the whole column data.

The query `SELECT count(n) FROM table` SHALL be transformed to `SELECT sum(NOT n.null) FROM table`.

##### min

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Min
version: 1.0

[ClickHouse] SHALL support [min] standard aggregate function.

##### max

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Max
version: 1.0

[ClickHouse] SHALL support [max] standard aggregate function.

##### sum

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Sum
version: 1.0

[ClickHouse] SHALL support [sum] standard aggregate function.

##### avg

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Avg
version: 1.0

[ClickHouse] SHALL support [avg] standard aggregate function.

##### any

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.Any
version: 1.0

[ClickHouse] SHALL support [any] standard aggregate function.

##### stddevPop

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.StddevPop
version: 1.0

[ClickHouse] SHALL support [stddevPop] standard aggregate function.

##### stddevSamp

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.StddevSamp
version: 1.0

[ClickHouse] SHALL support [stddevSamp] standard aggregate function.

##### varPop

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.VarPop
version: 1.0

[ClickHouse] SHALL support [varPop] standard aggregate function.

##### varSamp

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.VarSamp
version: 1.0

[ClickHouse] SHALL support [varSamp] standard aggregate function.

##### covarPop

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.CovarPop
version: 1.0

[ClickHouse] SHALL support [covarPop] standard aggregate function.

##### covarSamp

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Standard.CovarSamp
version: 1.0

[ClickHouse] SHALL support [covarSamp] standard aggregate function.

#### Specific Functions

##### anyHeavy

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.AnyHeavy
version: 1.0

[ClickHouse] SHALL support [anyHeavy] specific aggregate function.

##### anyLast

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.AnyLast
version: 1.0

[ClickHouse] SHALL support [anyLast] specific aggregate function.

##### argMin

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.ArgMin
version: 1.0

[ClickHouse] SHALL support [argMin] specific aggregate function.

##### argMax

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.ArgMax
version: 1.0

[ClickHouse] SHALL support [argMax] specific aggregate function.

##### avgWeighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.AvgWeighted
version: 1.0

[ClickHouse] SHALL support [avgWeighted] specific aggregate function.

##### topK

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.TopK
version: 1.0

[ClickHouse] SHALL support [topK] specific aggregate function.

##### topKWeighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.TopKWeighted
version: 1.0

[ClickHouse] SHALL support [topKWeighted] specific aggregate function.

##### groupArray

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArray
version: 1.0

[ClickHouse] SHALL support [groupArray] specific aggregate function.

##### groupArrayLast

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayLast
version: 1.0

[ClickHouse] SHALL support [groupArrayLast] specific aggregate function.

##### groupUniqArray

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupUniqArray
version: 1.0

[ClickHouse] SHALL support [groupUniqArray] specific aggregate function.

##### groupArrayInsertAt

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayInsertAt
version: 1.0

[ClickHouse] SHALL support [groupArrayInsertAt] specific aggregate function.

##### groupArrayMovingAvg

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayMovingAvg
version: 1.0

[ClickHouse] SHALL support [groupArrayMovingAvg] specific aggregate function.

##### groupArrayMovingSum

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArrayMovingSum
version: 1.0

[ClickHouse] SHALL support [groupArrayMovingSum] specific aggregate function.

##### groupArraySample

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupArraySample
version: 1.0

[ClickHouse] SHALL support [groupArraySample] specific aggregate function.

##### groupBitAnd

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitAnd
version: 1.0

[ClickHouse] SHALL support [groupBitAnd] specific aggregate function.

##### groupBitOr

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitOr
version: 1.0

[ClickHouse] SHALL support [groupBitOr] specific aggregate function.

##### groupBitXor

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitXor
version: 1.0

[ClickHouse] SHALL support [groupBitXor] specific aggregate function.

##### groupBitmap

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmap
version: 1.0

[ClickHouse] SHALL support [groupBitmap] specific aggregate function.

##### groupBitmapAnd

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmapAnd
version: 1.0

[ClickHouse] SHALL support [groupBitmapAnd] specific aggregate function.

##### groupBitmapOr

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmapOr
version: 1.0

[ClickHouse] SHALL support [groupBitmapOr] specific aggregate function.

##### groupBitmapXor

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.GroupBitmapXor
version: 1.0

[ClickHouse] SHALL support [groupBitmapXor] specific aggregate function.

##### sumWithOverflow

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumWithOverflow
version: 1.0

[ClickHouse] SHALL support [sumWithOverflow] specific aggregate function.

##### sumMap

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumMap
version: 1.0

[ClickHouse] SHALL support [sumMap] specific aggregate function.

##### minMap

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MinMap
version: 1.0

[ClickHouse] SHALL support [minMap] specific aggregate function.

##### maxMap

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MaxMap
version: 1.0

[ClickHouse] SHALL support [maxMap] specific aggregate function.

##### skewSamp

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SkewSamp
version: 1.0

[ClickHouse] SHALL support [skewSamp] specific aggregate function.

##### skewPop

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SkewPop
version: 1.0

[ClickHouse] SHALL support [skewPop] specific aggregate function.

##### kurtSamp

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.KurtSamp
version: 1.0

[ClickHouse] SHALL support [kurtSamp] specific aggregate function.

##### kurtPop

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.KurtPop
version: 1.0

[ClickHouse] SHALL support [kurtPop] specific aggregate function.

##### uniq

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Uniq
version: 1.0

[ClickHouse] SHALL support [uniq] specific aggregate function.

##### uniqExact

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqExact
version: 1.0

[ClickHouse] SHALL support [uniqExact] specific aggregate function.

##### uniqCombined

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqCombined
version: 1.0

[ClickHouse] SHALL support [uniqCombined] specific aggregate function.

##### uniqCombined64

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqCombined64
version: 1.0

[ClickHouse] SHALL support [uniqCombined64] specific aggregate function.

##### uniqHLL12

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.UniqHLL12
version: 1.0

[ClickHouse] SHALL support [uniqHLL12] specific aggregate function.

##### quantile

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Quantile
version: 1.0

[ClickHouse] SHALL support [quantile] specific aggregate function.

##### quantiles

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Quantiles
version: 1.0

[ClickHouse] SHALL support [quantiles] specific aggregate function.

##### quantilesExactExclusive

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactExclusive
version: 1.0

[ClickHouse] SHALL support [quantilesExactExclusive] specific aggregate function.

##### quantilesExactInclusive

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactInclusive
version: 1.0

[ClickHouse] SHALL support [quantilesExactInclusive] specific aggregate function.

##### quantilesDeterministic

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesDeterministic
version: 1.0

[ClickHouse] SHALL support [quantilesDeterministic] specific aggregate function.

##### quantilesExact

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExact
version: 1.0

[ClickHouse] SHALL support [quantilesExact] specific aggregate function.

##### quantilesExactHigh

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactHigh
version: 1.0

[ClickHouse] SHALL support [quantilesExactHigh] specific aggregate function.

##### quantilesExactLow

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactLow
version: 1.0

[ClickHouse] SHALL support [quantilesExactLow] specific aggregate function.

##### quantilesExactWeighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesExactWeighted
version: 1.0

[ClickHouse] SHALL support [quantilesExactWeighted] specific aggregate function.

##### quantilesTDigest

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTDigest
version: 1.0

[ClickHouse] SHALL support [quantilesTDigest] specific aggregate function.

##### quantilesTDigestWeighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTDigestWeighted
version: 1.0

[ClickHouse] SHALL support [quantilesTDigestWeighted] specific aggregate function.

##### quantilesBFloat16

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesBFloat16
version: 1.0

[ClickHouse] SHALL support [quantilesBFloat16] specific aggregate function.

##### quantilesBFloat16Weighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesBFloat16Weighted
version: 1.0

[ClickHouse] SHALL support [quantilesBFloat16Weighted] specific aggregate function.

##### quantilesTiming

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTiming
version: 1.0

[ClickHouse] SHALL support [quantilesTiming] specific aggregate function.

##### quantilesTimingWeighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesTimingWeighted
version: 1.0

[ClickHouse] SHALL support [quantilesTimingWeighted] specific aggregate function.

##### quantilesGK

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesGK
version: 1.0

[ClickHouse] SHALL support [quantilesGK] specific aggregate function.

##### quantilesInterpolatedWeighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantilesInterpolatedWeighted
version: 1.0

[ClickHouse] SHALL support `quantilesInterpolatedWeighted` specific aggregate function.

##### quantileExact

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExact
version: 1.0

[ClickHouse] SHALL support [quantileExact] specific aggregate function.

##### quantileExactLow

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExactLow
version: 1.0

[ClickHouse] SHALL support [quantileExactLow] specific aggregate function.

##### quantileExactHigh

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExactHigh
version: 1.0

[ClickHouse] SHALL support [quantileExactHigh] specific aggregate function.

##### quantileExactWeighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileExactWeighted
version: 1.0

[ClickHouse] SHALL support [quantileExactWeighted] specific aggregate function.

##### quantileTiming

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTiming
version: 1.0

[ClickHouse] SHALL support [quantileTiming] specific aggregate function.

##### quantileTimingWeighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTimingWeighted
version: 1.0

[ClickHouse] SHALL support [quantileTimingWeighted] specific aggregate function.

##### quantileDeterministic

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileDeterministic
version: 1.0

[ClickHouse] SHALL support [quantileDeterministic] specific aggregate function.

##### quantileTDigest

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTDigest
version: 1.0

[ClickHouse] SHALL support [quantileTDigest] specific aggregate function.

##### quantileTDigestWeighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileTDigestWeighted
version: 1.0

[ClickHouse] SHALL support [quantileTDigestWeighted] specific aggregate function.

##### quantileBFloat16

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileBFloat16
version: 1.0

[ClickHouse] SHALL support [quantileBFloat16] specific aggregate function.

##### quantileBFloat16Weighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileBFloat16Weighted
version: 1.0

[ClickHouse] SHALL support [quantileBFloat16Weighted] specific aggregate function.

##### quantileInterpolatedWeighted

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileInterpolatedWeighted
version: 1.0

[ClickHouse] SHALL support [quantileInterpolatedWeighted] specific aggregate function.

##### quantileGK

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.QuantileGK
version: 1.0

[ClickHouse] SHALL support [quantileGK] specific aggregate function.

##### simpleLinearRegression

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SimpleLinearRegression
version: 1.0

[ClickHouse] SHALL support [simpleLinearRegression] specific aggregate function.

##### stochasticLinearRegression

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.StochasticLinearRegression
version: 1.0

[ClickHouse] SHALL support [stochasticLinearRegression] specific aggregate function.

##### stochasticLogisticRegression

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.StochasticLogisticRegression
version: 1.0

[ClickHouse] SHALL support [stochasticLogisticRegression] specific aggregate function.

##### categoricalInformationValue

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.CategoricalInformationValue
version: 1.0

[ClickHouse] SHALL support [categoricalInformationValue] specific aggregate function.

##### studentTTest

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.StudentTTest
version: 1.0

[ClickHouse] SHALL support [studentTTest] specific aggregate function.

##### welchTTest

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.WelchTTest
version: 1.0

[ClickHouse] SHALL support [welchTTest] specific aggregate function.

##### mannWhitneyUTest

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MannWhitneyUTest
version: 1.0

[ClickHouse] SHALL support [mannWhitneyUTest] specific aggregate function.

##### median

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Median
version: 1.0

[ClickHouse] SHALL support [median] specific aggregate function.

##### rankCorr

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.RankCorr
version: 1.0

[ClickHouse] SHALL support [rankCorr] specific aggregate function.

##### entropy

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Entropy
version: 1.0

[ClickHouse] SHALL support [entropy] specific aggregate function.

##### meanZTest

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.MeanZTest
version: 1.0

[ClickHouse] SHALL support [meanZTest] specific aggregate function.

##### sparkbar

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Sparkbar
version: 1.0

[ClickHouse] SHALL support [sparkbar] specific aggregate function.

##### corr

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.Corr
version: 1.0

[ClickHouse] SHALL support [corr] specific aggregate function.

##### deltaSum

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.DeltaSum
version: 1.0

[ClickHouse] SHALL support [deltaSum] specific aggregate function.

##### deltaSumTimestamp

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.DeltaSumTimestamp
version: 1.0

[ClickHouse] SHALL support [deltaSumTimestamp] specific aggregate function.

##### exponentialMovingAverage

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.ExponentialMovingAverage
version: 1.0

[ClickHouse] SHALL support [exponentialMovingAverage] specific aggregate function.

##### intervalLengthSum

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.IntervalLengthSum
version: 1.0

[ClickHouse] SHALL support [intervalLengthSum] specific aggregate function.

#### kolmogorovSmirnovTest

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.KolmogorovSmirnovTest
version: 1.0

[ClickHouse] SHALL support [kolmogorovSmirnovTest] specific aggregate function.

##### sumCount

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumCount
version: 1.0

[ClickHouse] SHALL support [sumCount] specific aggregate function.

##### sumKahan

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.SumKahan
version: 1.0

[ClickHouse] SHALL support [sumKahan] specific aggregate function.

##### corrMatrix

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.CorrMatrix
version: 1.0

[ClickHouse] SHALL support [corrMatrix] specific aggregate function.

##### covarSampMatrix

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.CovarSampMatrix
version: 1.0

[ClickHouse] SHALL support [covarSampMatrix] specific aggregate function.

##### covarPopMatrix

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Specific.CovarPopMatrix
version: 1.0

[ClickHouse] SHALL support [covarPopMatrix] specific aggregate function.

#### Miscellaneous Functions

##### first_value

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.FirstValue
version: 1.0

[ClickHouse] SHALL support `first_value` aggregate function.

##### first_value_respect_nulls

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.FirstValueRespectNulls
version: 1.0

[ClickHouse] SHALL support `first_value_respect_nulls` aggregate function.

##### last_value

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LastValue
version: 1.0

[ClickHouse] SHALL support `last_value` aggregate function.

##### last_value_respect_nulls

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LastValueRespectNulls
version: 1.0

[ClickHouse] SHALL support `last_value_respect_nulls` aggregate function.

##### lagInFrame

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LagInFrame
version: 1.0

[ClickHouse] SHALL support `lagInFrame` aggregate function.

##### leadInFrame

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.LeadInFrame
version: 1.0

[ClickHouse] SHALL support `leadInFrame` aggregate function.

##### nth_value

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.NthValue
version: 1.0

[ClickHouse] SHALL support `nth_value` aggregate function.

##### rank

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Rank
version: 1.0

[ClickHouse] SHALL support `rank` aggregate function.

##### row_number

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.RowNumber
version: 1.0

[ClickHouse] SHALL support `row_number` aggregate function.

##### ntile

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Ntile
version: 1.0

[ClickHouse] SHALL support `ntile` aggregate function.

##### singleValueOrNull

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SingleValueOrNull
version: 1.0

[ClickHouse] SHALL support `singleValueOrNull` aggregate function.

##### maxIntersections

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MaxIntersections
version: 1.0

[ClickHouse] SHALL support `maxIntersections` aggregate function.

##### maxIntersectionsPosition

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MaxIntersectionsPosition
version: 1.0

[ClickHouse] SHALL support `maxIntersectionsPosition` aggregate function.

##### aggThrow

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.AggThrow
version: 1.0

[ClickHouse] SHALL support `aggThrow` aggregate function.

##### boundingRatio

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.BoundingRatio
version: 1.0

[ClickHouse] SHALL support `boundingRatio` aggregate function.

##### contingency

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Contingency
version: 1.0

[ClickHouse] SHALL support `contingency` aggregate function.

##### cramersV

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.CramersV
version: 1.0

[ClickHouse] SHALL support `cramersV` aggregate function.

##### cramersVBiasCorrected

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.CramersVBiasCorrected
version: 1.0

[ClickHouse] SHALL support `cramersVBiasCorrected` aggregate function.

##### dense_rank

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.DenseRank
version: 1.0

[ClickHouse] SHALL support `dense_rank` aggregate function.

##### exponentialTimeDecayedAvg

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedAvg
version: 1.0

[ClickHouse] SHALL support `exponentialTimeDecayedAvg` aggregate function.

##### exponentialTimeDecayedCount

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedCount
version: 1.0

[ClickHouse] SHALL support `exponentialTimeDecayedCount` aggregate function.

##### exponentialTimeDecayedMax

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedMax
version: 1.0

[ClickHouse] SHALL support `exponentialTimeDecayedMax` aggregate function.

##### exponentialTimeDecayedSum

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.ExponentialTimeDecayedSum
version: 1.0

[ClickHouse] SHALL support `exponentialTimeDecayedSum` aggregate function.

##### uniqTheta

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.UniqTheta
version: 1.0

[ClickHouse] SHALL support `uniqTheta` aggregate function.

##### quantileExactExclusive

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.QuantileExactExclusive
version: 1.0

[ClickHouse] SHALL support `quantileExactExclusive` aggregate function.

##### quantileExactInclusive

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.QuantileExactInclusive
version: 1.0

[ClickHouse] SHALL support `quantileExactInclusive` aggregate function.

##### sumMapFilteredWithOverflow

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SumMapFilteredWithOverflow
version: 1.0

[ClickHouse] SHALL support `sumMapFilteredWithOverflow` aggregate function.

##### sumMapWithOverflow

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SumMapWithOverflow
version: 1.0

[ClickHouse] SHALL support `sumMapWithOverflow` aggregate function.

##### sumMappedArrays

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.SumMappedArrays
version: 1.0

[ClickHouse] SHALL support `sumMappedArrays` aggregate function.

##### nothing

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.Nothing
version: 1.0

[ClickHouse] SHALL support `nothing` aggregate function.

##### maxMappedArrays

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MaxMappedArrays
version: 1.0

[ClickHouse] SHALL support `maxMappedArrays` aggregate function.

##### minMappedArrays

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.MinMappedArrays
version: 1.0

[ClickHouse] SHALL support `minMappedArrays` aggregate function.

##### nonNegativeDerivative

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.NonNegativeDerivative
version: 1.0

[ClickHouse] SHALL support `nonNegativeDerivative` aggregate function.

##### theilsU

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.TheilsU
version: 1.0

[ClickHouse] SHALL support `theilsU` aggregate function.

##### analysisOfVariance

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.AnalysisOfVariance
version: 1.0

[ClickHouse] SHALL support [analysisOfVariance(anova)] aggregate function.

##### flameGraph

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Miscellaneous.FlameGraph
version: 1.0

[ClickHouse] SHALL support [flameGraph] aggregate function.

#### Parametric Functions

##### histogram

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.Histogram
version: 1.0

[ClickHouse] SHALL support [histogram] parameteric aggregate function.

##### sequenceMatch

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SequenceMatch
version: 1.0

[ClickHouse] SHALL support [sequenceMatch] parameteric aggregate function.

##### sequenceCount

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SequenceCount
version: 1.0

[ClickHouse] SHALL support [sequenceCount] parameteric aggregate function.

##### windowFunnel

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.WindowFunnel
version: 1.0

[ClickHouse] SHALL support [windowFunnel] parameteric aggregate function.

##### retention

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.Retention
version: 1.0

[ClickHouse] SHALL support [retention] parameteric aggregate function.

##### uniqUpTo

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.UniqUpTo
version: 1.0

[ClickHouse] SHALL support [uniqUpTo] parameteric aggregate function.

##### sumMapFiltered

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SumMapFiltered
version: 1.0

[ClickHouse] SHALL support [sumMapFiltered] parameteric aggregate function.

##### sequenceNextNode

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.SequenceNextNode
version: 1.0

[ClickHouse] SHALL support [sequenceNextNode] parameteric aggregate function.

##### largestTriangleThreeBuckets

###### RQ.SRS-031.ClickHouse.AggregateFunctions.Parametric.LargestTriangleThreeBuckets
version: 1.0

[ClickHouse] SHALL support [largestTriangleThreeBuckets] parameteric aggregate function.

### Combinator Functions

#### -If Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.If
version: 1.0

[ClickHouse] SHALL support [-If] combinator suffix for all [aggregate function]s which
SHALL enable the aggregate function to accept an extra argument – a condition of `Uint8` type.
The aggregate function SHALL process only the rows that trigger the condition.
If the condition was not triggered even once, the function SHALL return a default value.

For example,

```sql
sumIf(column, cond)
countIf(cond)
avgIf(x, cond)
quantilesTimingIf(level1, level2)(x, cond)
argMinIf(arg, val, cond)
...
```

#### -Array Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Array
version: 1.0

[ClickHouse] SHALL support [-Array] combinator suffix for all [aggregate function]s which
SHALL enable the aggregate function ti take arguments of the `Array(T)` type (arrays)
instead of `T` type arguments.

If the aggregate function accepts multiple arguments, the arrays SHALL be of equal lengths.
When processing arrays, the aggregate function SHALL work like the original
aggregate function across all array elements.

For example,

```sql
sumArray(arr) -- sum all the elements of all ‘arr’ arrays
```

```sql
uniqArray(arr) -- count the number of unique elements in all ‘arr’ arrays
```

#### -Map Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Map
version: 1.0

[ClickHouse] SHALL support [-Map] combinator suffix for all [aggregate function]s which
SHALL cause the aggregate function to take `Map` type as an argument,
and SHALL aggregate values of each key of the map separately using the specified aggregate function.

The result SHALL also be of a `Map` type.

For example,

```sql
sumMap(map(1,1))
avgMap(map('a', 1))
```

#### -State Suffix

##### Test Feature Diagram

```mermaid
flowchart LR
  subgraph -State
    direction TB
    subgraph A[Aggregate Functions]
        direction LR
        A1["all aggregate functions"]
        A2["all argument data types"]
    end
    subgraph B[Compatibility]
      direction LR
      B1["AggregatingMergeTree table engine"]
      B2["finalizeAggregation() function"]
      B3["runningAccumulate() function"]
      B4["-Merge functions"]
      B5["-MergeState functions"]
      B6["ArregateFunction data type"]
      B6["SimpleArregateFunction data type ?"]
      B7["Materialized View"]
    end
    subgraph CM[Output/Input]
      subgraph C[Output Formats]
      end
      subgraph D[Input Formats]
      end
    end
    subgraph E[ClickHouse versions]
      direction LR
      E1[Upgrade]
      E2[Downgrade]
    end
    subgraph F[Backups]
      direction LR
      F1[clickhouse-backup utility]
      F2[BACKUP TABLE .. TO statement] 
    end
  end
```

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State
version: 1.0

[ClickHouse] SHALL support [-State] combinator suffix for all [aggregate function]s which
SHALL return an intermediate state of the aggregation that user SHALL be able to use for
further processing or stored in a table to finish aggregation later.

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.AggregatingMergeTree
version: 1.0

[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator
with [AggregatingMergeTree] table engine.

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.InitializeAggregationFunction
version: 1.0

[ClickHouse]'s SHALL support using all [aggregate function]s with [initializeAggregation] function. 

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.FinalizeAggregationFunction
version: 1.0

[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator
with [finalizeAggregation] function.

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.RunningAccumulateFunction
version: 1.0

[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator
with [runningAccumulate] function.

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.Merge
version: 1.0

[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator
with the corresponding [-Merge] combinator function.

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.MergeState
version: 1.0

[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator
with the corresponding [-MergeState] combinator function.

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.AggregateFunctionDataType
version: 1.0

[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator
with [AggregateFunction] data type columns.

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.State.With.MaterializedView
version: 1.0

[ClickHouse]'s SHALL support using all [aggregate function]s with [-State] combinator
with [Materialized View] table engine.

#### -SimpleState Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.SimpleState
version: 1.0

[ClickHouse] SHALL support [-SimpleState] combinator suffix for all [aggregate function]s which
SHALL return the same result as the aggregate function but with a [SimpleAggregateFunction] data type.

For example,

```sql
WITH anySimpleState(number) AS c SELECT toTypeName(c), c FROM numbers(1)
```

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.SimpleState.With.AggregatingMergeTree
version: 1.0

[ClickHouse]'s SHALL support using all [aggregate function]s with [-SimpleState] combinator
with [AggregatingMergeTree] table engine to store data in a column with [SimpleAggregateFunction] data type.

#### -Merge Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Merge
version: 1.0

[ClickHouse] SHALL support [-Merge] combinator suffix for all [aggregate function]s which
SHALL cause the aggregate function to take the intermediate aggregation state as an argument and
combine the states to finish aggregation and the function SHALL return the resulting value.

#### -MergeState Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.MergeState
version: 1.0

[ClickHouse] SHALL support [-MergeState] combinator suffix for all [aggregate function]s which
SHALL cause the aggregate function to merge the intermediate aggregation states in the same way as the
[-Merge] combinator but SHALL return an intermediate aggregation state, similar to the [-State] combinator.

#### -ForEach Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.ForEach
version: 1.0

[ClickHouse] SHALL support [-MergeState] combinator suffix for all [aggregate function]s which
SHALL convert aggregate function for tables into an aggregate function for arrays
that SHALL aggregate the corresponding array items and SHALL return an array of results.

For example,

> sumForEach for the arrays [1, 2], [3, 4, 5] and [6, 7] SHALL return the result [10, 13, 5]
> after adding together the corresponding array items

#### -Distinct Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Distinct
version: 1.0

[ClickHouse] SHALL support [-Distinct] combinator suffix for all [aggregate function]s which
SHALL cause the aggregate function for every unique combination of arguments to be aggregated only once.

Repeating values SHALL be ignored.

For example,

```sql
sum(DISTINCT x)
groupArray(DISTINCT x)
corrStableDistinct(DISTINCT x, y)
```

#### -OrDefault Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.OrDefault
version: 1.0

[ClickHouse] SHALL support [-OrDefault] combinator suffix for all [aggregate function]s which
SHALL change the behavior of an aggregate function.

If an aggregate function does not have input values, with this combinator it SHALL return
the default value for its return data type.

This combinator SHALL apply to the aggregate functions that can take empty input data.

The `-OrDefault` SHALL support to be used with other combinators which
SHALL enable to use aggregate function which do not accept the empty input.

Syntax:

```sql
[aggregate function]OrDefault(x)
```

where `x` are the aggregate function parameters.

The function SHALL return the default value of an aggregate function’s return type if there is nothing to aggregate
and the type SHALL depend on the aggregate function used.

For example, 

```sql
SELECT avg(number), avgOrDefault(number) FROM numbers(0)
```

SHALL produce the following output

```bash
┌─avg(number)─┬─avgOrDefault(number)─┐
│         nan │                    0 │
└─────────────┴──────────────────────┘
```

For example,

```sql
SELECT avgOrDefaultIf(x, x > 10)
FROM
(
    SELECT toDecimal32(1.23, 2) AS x
)
```

SHALL produce the following output

```bash
┌─avgOrDefaultIf(x, greater(x, 10))─┐
│                              0.00 │
└───────────────────────────────────┘
```

#### -OrNull Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.OrNull
version: 1.0

[ClickHouse] SHALL support [--OrNull] combinator suffix for all [aggregate function]s which
SHALL change the behavior of an aggregate function.

The combinator SHALL convert a result of an aggregate function to the `Nullable` data type.
If the aggregate function does not have values to calculate it SHALL return `NULL`.

Syntax:

```sql
<aggregate function>OrNull(x)
```

where `x` is aggregate function parameters.

In addition, the [-OrNull] combinator SHALL support to be used with other combinators
which SHALL enable to use aggregate function which do not accept the empty input.

For example,

```sql
SELECT sumOrNull(number), toTypeName(sumOrNull(number)) FROM numbers(10) WHERE number > 10
```

SHALL produce the following output

```bash
┌─sumOrNull(number)─┬─toTypeName(sumOrNull(number))─┐
│              ᴺᵁᴸᴸ │ Nullable(UInt64)              │
└───────────────────┴───────────────────────────────┘
```

For example,

```sql
SELECT avgOrNullIf(x, x > 10)
FROM
(
    SELECT toDecimal32(1.23, 2) AS x
)
```

SHALL produce the following output

```bash
┌─avgOrNullIf(x, greater(x, 10))─┐
│                           ᴺᵁᴸᴸ │
└────────────────────────────────┘
```

#### -Resample Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.Resample
version: 1.0

[ClickHouse] SHALL support [-Resample] combinator suffix for all [aggregate function]s which
SHALL cause the aggregate function to divide data into groups, and then it SHALL separately aggregate
the data in those groups. Groups SHALL be created by splitting the values from one column into intervals.

The function SHALL return an `Array` of aggregate function results for each sub-interval.

Syntax:

```sql
<aggregate function>Resample(start, end, step)(<aggFunction_params>, resampling_key)
```

where arguments SHALL be the following

* `start`  starting value of the whole required interval for resampling_key values
* `stop`  ending value of the whole required interval for resampling_key values
  The whole interval does not include the stop value [start, stop)
* `step` step for separating the whole interval into sub-intervals.
  The aggregate function is executed over each of those sub-intervals independently.
* `resampling_key` column whose values are used for separating data into intervals
* `aggFunction_params` aggregate function parameters

For example, 

with `people` table containing

```bash
┌─name───┬─age─┬─wage─┐
│ John   │  16 │   10 │
│ Alice  │  30 │   15 │
│ Mary   │  35 │    8 │
│ Evelyn │  48 │ 11.5 │
│ David  │  62 │  9.9 │
│ Brian  │  60 │   16 │
└────────┴─────┴──────┘
```

```sql
SELECT groupArrayResample(30, 75, 30)(name, age) FROM people
```

SHALL produce the following result

```bash
┌─groupArrayResample(30, 75, 30)(name, age)─────┐
│ [['Alice','Mary','Evelyn'],['David','Brian']] │
└───────────────────────────────────────────────┘
```

and

```sql
SELECT
    countResample(30, 75, 30)(name, age) AS amount,
    avgResample(30, 75, 30)(wage, age) AS avg_wage
FROM people
```

SHALL produce

```bash
┌─amount─┬─avg_wage──────────────────┐
│ [3,2]  │ [11.5,12.949999809265137] │
└────────┴───────────────────────────┘
```

#### --ArgMin Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.ArgMin
version: 1.0

[ClickHouse] SHALL support [-ArgMin] combinator suffix for all [aggregate function]s which
SHALL cause the aggregate function to process only the rows that have the minimum value for the specified extra expression. The aggregate function with combinator SHALL accept an additional argument, which should be any comparable expression.

For example, sumArgMin(column, expr), countArgMin(expr), avgArgMin(x, expr).

#### --ArgMax Suffix

##### RQ.SRS-031.ClickHouse.AggregateFunctions.Combinator.ArgMax
version: 1.0

[ClickHouse] SHALL support [-ArgMax] combinator suffix for all [aggregate function]s which
SHALL cause the aggregate function to process only the rows that have the maximum value for the specified extra expression. The aggregate function with combinator SHALL accept an additional argument, which should be any comparable expression.

### Data Types

#### SimpleAggregateFunction

##### RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.SimpleAggregateFunction
version: 1.0

[ClickHouse] SHALL support [SimpleAggregateFunction] data type which SHALL allow to store a
current value of the aggregate function. 

This function SHALL be used as optimization to [AggregateFunction] when the following property holds: 

> the result of applying a function f to a row set S1 UNION ALL S2 can be obtained by applying f to parts of the row set
> separately, and then again applying f to the results: f(S1 UNION ALL S2) = f(f(S1) UNION ALL f(S2)).
> This property guarantees that partial aggregation results are enough to compute the combined one,
> so we do not have to store and process any extra data.

#### AggregateFunction

##### RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.AggregateFunction
version: 1.0

[ClickHouse] SHALL support [AggregateFunction] data type which SHALL allow to store as a table column
implementation-defined intermediate state of the specified [aggregate function].

The data type SHALL be defined using the following syntax:

```sql
AggregateFunction(name, types_of_arguments…).
```

where parameters

* `name` SHALL specify the aggregate function and if the function is parametric the parameters SHALL be specified as well
* `types_of_arguments` SHALL specify types of the aggregate function arguments.

For example,

```sql
CREATE TABLE t
(
    column1 AggregateFunction(uniq, UInt64),
    column2 AggregateFunction(anyIf, String, UInt8),
    column3 AggregateFunction(quantiles(0.5, 0.9), UInt64)
) ENGINE = ...
```

##### Inserting Data

###### RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.AggregateFunction.Insert

[ClickHouse] SHALL support inserting data into [AggregateFunction] data type column 
using a value returned by calling the [aggregate function] with the `-State` suffix in
`INSERT SELECT` statement.

For example,

```sql
INSERT INTO table SELECT uniqState(UserID), quantilesState(0.5, 0.9)(SendTiming)
```

##### Selecting Data

###### RQ.SRS-031.ClickHouse.AggregateFunctions.DataType.AggregateFunction.Select

[ClickHouse] SHALL support selecting final result of aggregation from [AggregateFunction] data type column
by using the same [aggregate function] with the `-Merge` suffix.

For example,

```sql
SELECT uniqMerge(state) FROM (SELECT uniqState(UserID) AS state FROM table GROUP BY RegionID)
```

### Grouping

#### RQ.SRS-031.ClickHouse.AggregateFunctions.Grouping

[ClickHouse] SHALL support `GROUPING` function which SHALL take multiple columns as an argument and SHALL
return a bitmask where bits SHALL indicate the following

* `1` that a row returned by a `ROLLUP` or `CUBE` modifier to `GROUP BY` is a subtotal
* `0` that a row returned by a `ROLLUP` or `CUBE` is a row that is not a subtotal

### Grouping Sets

#### RQ.SRS-031.ClickHouse.AggregateFunctions.GroupingSets

[ClickHouse] SHALL support `GROUPING SETS` which SHALL allow user to specify the specific combinations to calculate
as by default, the `CUBE` modifier calculates subtotals for all possible combinations of the columns passed to
`CUBE`.

For example,

```sql
SELECT
    datacenter,
    distro, 
    SUM (quantity) qty
FROM
    servers
GROUP BY
    GROUPING SETS(
        (datacenter,distro),
        (datacenter),
        (distro),
        ()
    )
```

## References

* [ClickHouse]
* [GitHub Repository]
* [Revision History]
* [Git]

[MergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree/
[Materialized View]: https://clickhouse.com/docs/en/sql-reference/statements/create/view#materialized-view
[-MergeState]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/combinators#-mergestate
[-Merge]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/combinators#-merge
[-SimpleState]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/combinators#-simplestate
[-State]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/combinators#-state
[-ArgMin]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/combinators#-argmin
[-ArgMax]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/combinators#-argmax
[runningAccumulate]: https://clickhouse.com/docs/en/sql-reference/functions/other-functions#runningaccumulate
[initializeAggregation]: https://clickhouse.com/docs/en/sql-reference/functions/other-functions#initializeaggregation
[finalizeAggregation]: https://clickhouse.com/docs/en/sql-reference/functions/other-functions#function-finalizeaggregation
[AggregatingMergeTree]: https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/aggregatingmergetree
[aggregate function]: #aggregate-functions
[SimpleAggregateFunction]: https://clickhouse.com/docs/en/sql-reference/data-types/simpleaggregatefunction
[AggregateFunction]: https://clickhouse.com/docs/en/sql-reference/data-types/aggregatefunction
[ClickHouse]: https://clickhouse.com
[GitHub Repository]: https://github.com/Altinity/clickhouse-regression/blob/main/aggregate_functions/requirements/requirements.md
[Revision History]: https://github.com/Altinity/clickhouse-regression/commits/main/aggregate_functions/requirements/requirements.md
[Git]: https://git-scm.com/
[GitHub]: https://github.com
[count]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/count/
[min]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/min/
[max]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/max/
[sum]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/sum/
[avg]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/avg/
[any]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/any/
[stddevPop]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/stddevpop/
[stddevSamp]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/stddevsamp/
[varPop]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/varpop/
[varSamp]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/varsamp/
[covarPop]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/covarpop/
[covarSamp]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/covarsamp/
[anyHeavy]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/anyheavy/
[anyLast]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/anylast/
[argMin]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/argmin/
[argMax]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/argmax/
[avgWeighted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/avgweighted/
[corr]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/corr/
[topK]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/topk/
[topKWeighted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/topkweighted/
[groupArray]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/grouparray/
[groupArrayLast]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/grouparraylast
[groupUniqArray]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/groupuniqarray/
[groupArrayInsertAt]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/grouparrayinsertat/
[groupArrayMovingSum]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/grouparraymovingsum/
[groupArrayMovingAvg]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/grouparraymovingavg/
[groupArraySample]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/grouparraysample/
[groupBitAnd]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/groupbitand/
[groupBitOr]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/groupbitor/
[groupBitXor]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/groupbitxor/
[groupBitmap]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/groupbitmap/
[groupBitmapAnd]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/groupbitmapand/
[groupBitmapOr]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/groupbitmapor/
[groupBitmapXor]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/groupbitmapxor/
[sumWithOverflow]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/sumwithoverflow/
[deltaSum]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/deltasum/
[deltaSumTimestamp]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/deltasumtimestamp
[sumMap]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/summap/
[minMap]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/minmap/
[maxMap]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/maxmap/
[initializeAggregation]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/initializeAggregation/
[skewPop]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/skewpop/
[skewSamp]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/skewsamp/
[kurtPop]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/kurtpop/
[kurtSamp]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/kurtsamp/
[uniq]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/uniq/
[uniqExact]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/uniqexact/
[uniqCombined]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/uniqcombined/
[uniqCombined64]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/uniqcombined64/
[uniqHLL12]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/uniqhll12/
[quantile]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantile/
[quantiles]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesExactExclusive]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles#quantilesexactexclusive
[quantilesExactInclusive]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles#quantilesexactinclusive
[quantilesDeterministic]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesExact]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesExactHigh]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesExactLow]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesExactWeighted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesTDigest]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesTDigestWeighted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesBFloat16]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesBFloat16Weigted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesTiming]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesTimingWeighted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles/
[quantilesGK]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiles#quantilesgk
[quantileExact]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantileexact/
[quantileExactWeighted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantileexactweighted/
[quantileTiming]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiletiming/
[quantileTimingWeighted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiletimingweighted/
[quantileDeterministic]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiledeterministic/
[quantileTDigest]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiletdigest/
[quantileTDigestWeighted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantiletdigestweighted/
[quantileBFloat16]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantilebfloat16
[quantileInterpolatedWeighted]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantileInterpolatedWeighted
[quantilebfloat16]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantilebfloat16
[quantileGK]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/quantileGK
[simpleLinearRegression]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/simplelinearregression/
[stochasticLinearRegression]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/stochasticlinearregression/
[stochasticLogisticRegression]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/stochasticlogisticregression/
[categoricalInformationValue]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/stochasticlogisticregression/
[studentTTest]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/studentttest/
[welchTTest]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/welchttest/
[mannWhitneyUTest]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/mannwhitneyutest/
[median]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/median/
[rankCorr]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/rankCorr/
[histogram]:https://clickhouse.com/docs/en/sql-reference/aggregate-functions/parametric-functions/#histogram
[largestTriangleThreeBuckets]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/largestTriangleThreeBuckets
[sequenceMatch]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/parametric-functions/#function-sequencematch
[sequenceCount]:https://clickhouse.com/docs/en/sql-reference/aggregate-functions/parametric-functions/#function-sequencecount
[windowFunnel]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/parametric-functions/#windowfunnel
[retention]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/parametric-functions/#retention
[uniqUpTo]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/parametric-functions/#uniquptonx
[sumMapFiltered]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/parametric-functions/#summapfilteredkeys-to-keepkeys-values
[sequenceNextNode]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/parametric-functions#sequencenextnode
[entropy]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/entropy
[meanZTest]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/meanztest
[sparkbar]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/sparkbar
[exponentialMovingAverage]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/exponentialmovingaverage
[intervalLengthSum]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/intervalLengthSum
[sumCount]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/sumcount
[sumKahan]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/sumkahan
[kolmogorovSmirnovTest]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/kolmogorovsmirnovtest
[theilsU]: https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/theilsu
[analysisOfVariance(anova)]: https://github.com/ClickHouse/ClickHouse/pull/42131
[flameGraph]: https://github.com/ClickHouse/ClickHouse/pull/38953
[corrMatrix]: https://github.com/ClickHouse/ClickHouse/pull/44680
[covarSampMatrix]: https://github.com/ClickHouse/ClickHouse/pull/44680
[covarPopMatrix]: https://github.com/ClickHouse/ClickHouse/pull/44680
