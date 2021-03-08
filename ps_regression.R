library(Matching)
library(estimatr)

df <- read.csv('predicted/df_dropped_na_with_ml.csv')

timedelta_mean <- mean(df$timedelta, na.rm=TRUE)
timedelta_mean
df <- transform(df, less_mean=df$timedelta<timedelta_mean)
df$less_mean[is.na(df$less_mean)] <- 0
df <- transform(df, over_mean=df$timedelta>=timedelta_mean)
df$over_mean[is.na(df$over_mean)] <- 0

P <- df$lgbm_pred


match <- with(df, Match(procurement_after, 
                        accelerator,
                        P,
                        Weight=1,
                        caliper=0.2,
                        )
              )


df_tmp <- df
df_tmp$id <- 1:nrow(df_tmp)
df_pair <- rbind(df_tmp[match$index.treated, c('id', colnames(df))],
                 df_tmp[match$index.control, c('id', colnames(df))]
                 )

df_pair$procurement_after <- log(df_pair$procurement_after+1e-07)

lm_res <- with(df_pair, lm_robust(procurement_after~less_mean+over_mean))
summary(lm_res)
filename <- 'result/ps_regression_ol.csv'
result <- with(lm_res, cbind(coefficients, std.error, statistic, p.value))
write.table(result, filename, append=TRUE, sep=',')
write.table(cbind('N', length(df$computer)), filename,
            append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
write.table(cbind('R-squared', lm_res$r.squared), filename, 
            append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
write.table(cbind('Adj R-squared', lm_res$adj.r.squared), filename,
            append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)


lm_acc <- with(df_pair, lm_robust(procurement_after~accelerator))
summary(lm_acc)
filename <- 'result/ps_regression_acc.csv'
result <- with(lm_acc, cbind(coefficients, std.error, statistic, p.value))
write.table(result, filename, append=TRUE, sep=',')
write.table(cbind('N', length(df$computer)), filename,
            append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
write.table(cbind('R-squared', lm_acc$r.squared), filename, 
            append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
write.table(cbind('Adj R-squared', lm_acc$adj.r.squared), filename,
            append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)