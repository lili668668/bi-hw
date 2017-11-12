library(arules)
library(Matrix)

options(width=200)

data <- read.table('data.csv', header = T, sep = ",")
data <- as.matrix(data)

rules <- apriori(data, parameter = list(supp = 0.2, conf = 0.6, target = "rules"))

new_rules <- subset(rules, subset=lhs%in%"年齡小於等於25" | rhs%in%"年齡小於等於25")

inspect(new_rules)
