library(arules)
library(Matrix)

data <- read.table('data.csv', header = T, sep = ",")
data <- as.matrix(data)
data <- data[,c(-1, -2, -3, -4)]

itemsets <- apriori(data, parameter = list(supp = 0.2, conf = 0.6, target = "frequent itemsets"))

inspect(itemsets)
