library(arules)
library(Matrix)

options(width=200)

data <- read.table('data.csv', header = T, sep = ",")
data <- as.matrix(data)
data <- data[,c(-1, -2, -3, -4)]

rules <- apriori(data, parameter = list(supp = 0.2, conf = 0.6, target = "rules"))

inspect(rules)
