library(estimatr)

df <- read.csv('dataset/df_dropped_na.csv')

df$capital <- log(df$capital+1e-7)
df$procurement_before <- log(df$procurement_before+1e-7)
df$procurement_after <- log(df$procurement_after+1e-7)
df <- df[, colnames(df)!='timedelta']
df <- na.omit(df)
df$deeptech <- df$bio + df$energy_and_semiconductor
df$deeptech_acc <- df$deeptech * df$accelerator

model <- with(df, lm_robust(procurement_after~
                              accelerator+
                              capital+
                              university+
                              venture+
                              enterprise+
                              deeptech+
                              deeptech_acc
              )
)

summary(model)
filename <- 'result/20220818/regression_result_accelerator_effect_20220818.csv'
result <- with(model, cbind(coefficients, std.error, statistic, p.value))
write.table(result, filename, append=TRUE, sep=',')
write.table(cbind('N', length(df$computer)), filename,
            append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
write.table(cbind('R-squared', model$r.squared), filename, 
            append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
write.table(cbind('Adj R-squared', model$adj.r.squared), filename,
            append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)