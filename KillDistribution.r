library(ggplot2)
library(BayesFactor)

loadData <- function(){
  data <- read.table('kms.txt', header = FALSE, fill = FALSE, sep = '\t')
  names(data) <- c(
    'Alliance',
    'ShipID',
    'SystemID',
    'Days'
  )
  
  return(data)
}

relableAlliance <- function(data){
  data <- data[data$Alliance != 'PSC',] # remove psc losses
  top_five <- names(summary(data$Alliance)[1:5])
  if ('None' %in% top_five){
    top_five <- names(summary(data$Alliance)[1:6])
    top_five <- top_five[top_five != 'None']
  }
  
  levels(data$Alliance) <- c(levels(data$Alliance), 'Misc')
  
  for (i in seq(length(data$Alliance))){
    if (!data$Alliance[i] %in% top_five){
      data$Alliance[i] <- 'Misc'
    }
  }
  return(data)
}

data <- loadData()
relabled_data <- relableAlliance(data)

ggplot(data = relabled_data[relabled_data$Alliance != 'Misc',]) + aes(x = Days, fill = Alliance) +
  # geom_density(adjust = 1/2) +
  geom_histogram(position = 'dodge', bins = 20)+
  xlab('Days since PSC formed') + 
  ylab('Kills from Alliance') + 
  geom_vline(aes(xintercept=0), color="red", linetype="dashed", size=1) +
  annotate('text', x = 5, y = 290, label = "left Brave to farm Brave", hjust = 0) +
  geom_vline(aes(xintercept=100), color="red", linetype="dashed", size=1) +
  annotate('text', x = 105, y = 200, label = "Joined SkillU", hjust = 0) +
  geom_vline(aes(xintercept=290), color="red", linetype="dashed", size=1) +
  annotate('text', x = 288, y = 250, label = "Operation Farm Brave", hjust = 1.0)
  