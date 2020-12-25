library(Matching)

less_mean <- read.csv('predicted/less_mean_with_ml.csv')

# 平均以下のデータセットについて
match <- with(less_mean, Match(procurement_after, 
                               accelerator,
                               lgbm_pred,
                               Weight=2,
                               caliper=0.2,
                              )
              )
summary(match)
filename <- 'result/less_mean_result.csv'
write.table(cbind('ESTIMATE', match$est), filename,
                  append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
write.table(cbind('SE', match$se), filename,
                  append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
t <- match$est / match$se
write.table(cbind('T-stat', t), filename,
                  append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
p <- 2 * (1 - pnorm(abs(t)))
write.table(cbind('p-value', p), filename,
                  append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
write.table(cbind('Original number of observations', match$orig.nobs), filename,
                  append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
write.table(cbind('Original number of treated obs', match$orig.treated.nobs), filename,
                  append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
write.table(cbind('SE', match$se), filename,
                  append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)


df_tmp <- less_mean
df_tmp$id <- 1:nrow(df_tmp)
df_pair <- cbind(df_tmp[match$index.treated, c('id', colnames(less_mean))],
                 df_tmp[match$index.control, c('id', colnames(less_mean))])
treat_cols <- list()
control_cols <- list()
for (i in 1: length(colnames(less_mean))){
  new_name <- paste0('treat_', colnames(less_mean)[i])
  treat_cols[i] <- new_name
  new_name <- paste0('control_', colnames(df)[i])
  control_cols[i] <- new_name
}
colnames(df_pair) = c('treat_id', treat_cols, 'control_id', control_cols)

for (col in c('capital',
              'procurement_before')){
  treat_colname <- paste0('treat_', col)
  control_colname <- paste0('control_', col)
  mean_treat <- mean(df_pair[, treat_colname], na.rm=TRUE)
  mean_control <- mean(df_pair[, control_colname], na.rm=TRUE)
  var_treat <- var(df_pair[, treat_colname], na.rm=TRUE)
  var_control <- var(df_pair[, control_colname], na.rm=TRUE)
  SD <- abs((mean_treat - mean_control) / sqrt((var_treat+var_control) / 2))
  print(paste0('SD_of_', col, ':', SD))
  print(paste0('Variance_ratio_of_', col,':', var_treat/var_control))
}


for (col in c('university',
              'venture',
              'enterprise',
              'energy_and_semiconductor',
              'finance',
              'ecology',
              'bio',
              'computer',
              'service')){
  treat_colname <- paste0('treat_', col)
  control_colname <- paste0('control_', col)
  mean_treat <- mean(df_pair[, treat_colname], na.rm=TRUE)
  mean_control <- mean(df_pair[, control_colname], na.rm=TRUE)
  SD <- abs((mean_treat - mean_control) / 
              sqrt((mean_treat*(1-mean_treat) + mean_control*(1-mean_control)) / 2))
  print(paste0('SD_of_', col, ':', SD))
}