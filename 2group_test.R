
df <- read.csv('dataset/df_dropped_na.csv')


# 等分散検定
var.test(df[df$accelerator==1, ]$procurement_after, 
         df[df$accelerator==0, ]$procurement_after)

# t検定（正規分布に従っていないため未使用）
t.test(procurement_after~accelerator, data=df, var.equal=TRUE)

# 正規性の検定
shapiro.test(df[df$accelerator==1, ]$procurement_after)
shapiro.test(df[df$accelerator==0, ]$procurement_after)


# Mann-WhiteneyのU検定
wilcox.test(df[df$accelerator==1, ]$procurement_after, 
            df[df$accelerator==0, ]$procurement_after)

result <- wilcox.test(df[df$accelerator==1, ]$procurement_after, 
            df[df$accelerator==0, ]$procurement_after)
filename <- 'result/Mann_whiteney_test.csv'
write.table(cbind('N', length(df$accelerator)), filename,
            append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
write.table(cbind('W', result$statistic), filename,
            append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)
write.table(cbind('p-value', result$p.value), filename,
            append=TRUE, sep=',', row.names=FALSE, col.names=FALSE)

