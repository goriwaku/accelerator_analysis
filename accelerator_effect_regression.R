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