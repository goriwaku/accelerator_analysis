df <- read.csv('dataset/df_dropped_na.csv')

df$capital <- log(df$capital+1e-7)
df$procurement_before <- log(df$procurement_before+1e-7)
df$procurement_after <- log(df$procurement_after+1e-7)
df <- na.omit(df)

model <- with(df, lm_robust(procurement_after~
                              accelerator+
                              capital+
                              university+
                              venture+
                              enterprise+
                              procurement_before+
                              energy_and_semiconductor+
                              finance+
                              computer+
                              service
              )
)

summary(model)
filename <- 'result/regression_result_accelerator_effect.csv'
result <- with(acc_model, cbind(coefficients, std.error, statistic, p.value))
write.table(result, filename, append=TRUE, sep=',')
write.table(cbind('N', length(df$computer)), filename,
            append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
write.table(cbind('R-squared', acc_model$r.squared), filename, 
            append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
write.table(cbind('Adj R-squared', acc_model$adj.r.squared), filename,
            append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)