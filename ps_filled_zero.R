library(Matching)

df <- read.csv('dataset/df_filled_na.csv')

result <- with(df, 
               glm(accelerator~
                     capital+
                     university+
                     venture+
                     enterprise+
                     procurement_before+
                     energy_and_semiconductor+
                     finance+
                     ecology+
                     bio+
                     computer+
                     service,
                   family=binomial(link='logit')))

P <- result$fitted


match <- with(df, Match(procurement_after, 
                        accelerator,
                        P,
                        Weight=1,
                        caliper=0.2,
                        #M=1,
                        #ties=FALSE
                        )
              )
summary(match)


df_tmp <- df
df_tmp$id <- 1:nrow(df_tmp)
df_pair <- cbind(df_tmp[match$index.treated, c('id', colnames(df))],
                 df_tmp[match$index.control, c('id', colnames(df))])
treat_cols <- list()
control_cols <- list()
for (i in 1: length(colnames(df))){
  new_name <- paste0('treat_', colnames(df)[i])
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
plot((df$accelerator-P))