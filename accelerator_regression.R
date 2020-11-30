library(estimatr)

df <- read.csv('dataset/dataset_for_regression.csv')
df$capital <- log(df$capital + 1e-07)
df$procurement_before <- log(df$procurement_before + 1e-07)
df$procurement_after <- log(df$procurement_after + 1e-07)
# df <- df[, colnames(df) != 'accelerator_type']
df <- na.omit(df)

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
                              accelerator_type
                  )
)

summary(acc_model)