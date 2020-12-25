library(estimatr)

df <- read.csv('dataset/dataset_for_regression.csv')
df$capital <- log(df$capital + 1e-07)
df$procurement_before <- log(df$procurement_before + 1e-07)
df$procurement_after <- log(df$procurement_after + 1e-07)
# df <- df[, colnames(df) != 'accelerator_type']
df <- na.omit(df)
timedelta_energy <- df$timedelta * df$energy_and_semiconductor
timedelta_finance <- df$timedelta * df$finance
timedelta_bio <- df$timedelta * df$bio
timedelta_computer <- df$timedelta * df$computer
timedelta_service <- df$timedelta * df$service
type_energy <- df$accelerator_type * df$energy_and_semiconductor
type_finance <- df$accelerator_type * df$finance
type_bio <- df$accelerator_type * df$bio
type_computer <- df$accelerator_type * df$computer
type_service <- df$accelerator_type * df$service

acc_model <- with(df, 
                  lm_robust(procurement_after~
                              capital+
                              university+
                              venture+
                              enterprise+
                              procurement_before+
                              timedelta+
                              energy_and_semiconductor+
                              finance+
                              computer+
                              service + 
                              accelerator_type+
                              timedelta_energy+
                              timedelta_finance+
                              timedelta_computer+
                              timedelta_service
                            #  type_energy+
                            #  type_finance+
                            #  type_computer+
                            #  type_service
                  )
)

summary(acc_model)
filename <- 'result/regression_result_timedelta.csv'
result <- with(acc_model, cbind(coefficients, std.error, statistic, p.value))
write.table(result, filename, append=TRUE, sep=',')
write.table(cbind('N', length(df$timedelta)), filename,
            append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
write.table(cbind('R-squared', acc_model$r.squared), filename, 
            append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
write.table(cbind('Adj R-squared', acc_model$adj.r.squared), filename,
            append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)