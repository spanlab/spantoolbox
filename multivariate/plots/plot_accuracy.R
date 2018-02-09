require(ggplot2)
library(dplyr)

setwd('/Users/span/spantoolbox/multivariate/plots')
csvs <- Sys.glob('*.csv')
df <- read.csv(csvs[1], header=F)
columns <- c("Subject", "Cval", "n_features", "Pct_features", "Accuracy")
colnames(df) <- columns


for(csv in csvs[-1]){
  to_add <- read.csv(csv, header=F)
  colnames(to_add) <- columns
  df <- rbind(df, to_add)
}

averages <- group_by(df, Cval, n_features) %>%
  summarize_all(.funs=mean)


ggplot(averages, aes(x=-Pct_features, y=Accuracy, color=as.factor(Cval))) +
  geom_point() + 
  geom_line()  + 
  ggtitle("Cross-validated accuracy with RFE")
ggsave('rfe_accuracy.png')
