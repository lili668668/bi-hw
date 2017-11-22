library(arules)
library(Matrix)

options(width=200)

data <- read.table('data.csv', header = T, sep = ",")
data <- as.matrix(data)

rules <- apriori(data, parameter = list(supp = 0.2, conf = 0.6, target = "rules"))

inspect(rules)
