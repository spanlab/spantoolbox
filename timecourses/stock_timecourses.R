library(ggplot2)
library(reshape2)
library(dplyr)

######### Helper Functions Stolen from the Internet ##########

simpleCap <- function(x) {
  ## Simple capitalization function
  s <- strsplit(x, " ")[[1]]
  paste(toupper(substring(s, 1,1)), substring(s, 2),
        sep="", collapse=" ")
}

library(plyr)
summarySE <- function(data=NULL, measurevar, groupvars=NULL, na.rm=FALSE,
                      conf.interval=.95, .drop=TRUE) {
  ##   Gives count, mean, standard deviation, standard error of the mean, and confidence interval (default 95%).
  ##   data: a data frame.
  ##   measurevar: the name of a column that contains the variable to be summariezed
  ##   groupvars: a vector containing names of columns that contain grouping variables
  ##   na.rm: a boolean that indicates whether to ignore NA's
  ##   conf.interval: the percent range of the confidence interval (default is 95%)
  
  # library(plyr)
  # New version of length which can handle NA's: if na.rm==T, don't count them
  length2 <- function (x, na.rm=TRUE) {
    if (na.rm) sum(!is.na(x))
    else       length(x)
  }
  
  # This does the summary. For each group's data frame, return a vector with
  # N, mean, and sd
  datac <- ddply(data, groupvars, .drop=.drop,
                 .fun = function(xx, col) {
                   c(N    = length2(xx[[col]], na.rm=na.rm),
                     mean = mean   (xx[[col]], na.rm=na.rm),
                     sd   = sd     (xx[[col]], na.rm=na.rm)
                   )
                 },
                 measurevar
  )
  
  # Rename the "mean" column    
  datac <- rename(datac, c("mean" = measurevar))
  
  datac$se <- datac$sd / sqrt(datac$N)  # Calculate standard error of the mean
  
  # Confidence interval multiplier for standard error
  # Calculate t-statistic for confidence interval: 
  # e.g., if conf.interval is .95, use .975 (above/below), and use df=N-1
  ciMult <- qt(conf.interval/2 + .5, datac$N-1)
  datac$ci <- datac$se * ciMult
  
  # detach(package:ddply)
  return(datac)
}

########## Basic Plotting Functions ################

standard_df <- function(df, grouping_vars=NULL) {
  plt <- summarySE(melt(df), measurevar="value", groupvars= grouping_vars, na.rm = TRUE)
  plt <- plt[sapply(plt$variable, function(x) grepl('TR_',x)),]
  plt$time <- 2 * (as.numeric(sapply(plt$variable, function(x) sub('TR_', '',x))) - 1)
  plt
}

standard_fg <- function(plt, color_var, fe=NULL) {
  fg <- ggplot(plt, aes_string(x='time', y='value', colour=color_var)) +
    geom_errorbar(aes(ymin=value-se, ymax=value+se), width=.5, position=pd) +
    geom_line(position=pd, aes_string(group=color_var,color=color_var)) +
    geom_point(position=pd, size=2, shape=21, fill="white") + # 21 is filled circle
    xlab("Seconds") +
    ylab("%\u0394 BOLD") +
    scale_y_continuous(breaks=-10:10*.1) +
    scale_x_continuous(breaks=c(seq(2,32, by=2))) +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
  if (!is.null(fe)) {
    fg <- fg + facet_grid(fe, scales="free")
  }
  fg
}

standard_title <- function(side, mask, ts) {
  bar_title = do.call(paste,as.list(sapply(c(side,mask, "\u0394 BOLD", ts, "- Bars"),simpleCap)))
  band_title = do.call(paste,as.list(sapply(c(side,mask, "\u0394 BOLD", ts, "- Bands"),simpleCap)))
  list('bar' = bar_title, 'band' = band_title)
}

standard_save <- function(plt, fg, tt, cv, wid=30, hgt=12) {
  #save bar
  fg <- fg + ggtitle(tt$bar)
  ggsave(file=paste0(tt$bar,'.png'), width = wid, height=hgt)
  
  #save band
  fg <- fg + geom_ribbon(data=plt, aes_string(ymin='value-se', ymax='value+se', alpha='.5',fill=cv), position=pd)
  fg <- fg + ggtitle(tt$band)
  ggsave(file=paste0(tt$band,'.png'), width = wid, height=hgt)
}



######### LOAD DATA ##########
user <- system('[ -f ~/i_am_mirre.txt ] && echo "Mirre" || echo "Nick"',  intern = TRUE)
if (user == 'Nick') {
  bias_scripts_dir <-  '/Users/span/projects/stockmri/stock_analysis/bias/r_scripts'
  bias_data_dir <- '/Users/span/projects/stockmri/stock_analysis/bias/data'
  stock_scripts_dir <-  '/Users/span/projects/stockmri/stock_analysis/stocks/r_scripts'
  stock_tc_dir <- '/Users/span/projects/stockmri/stock_analysis/stocks/timecourses'
  stock_data_dir <- '/Users/span/projects/stockmri/stock_analysis/stocks/data'
} else {
  bias_scripts_dir <- '/Users/span/Dropbox/Projects_Stanford/Neurochoice/Finance_project/fMRI_study/stock_analysis/bias/r_scripts'
  bias_data_dir <- '/Users/span/Dropbox/Projects_Stanford/Neurochoice/Finance_project/fMRI_study/stock_analysis/bias/data'
  stock_scripts_dir <- '/Users/span/Dropbox/Projects_Stanford/Neurochoice/Finance_project/fMRI_study/stock_analysis/stocks/r_scripts'
  stock_data_dir <- '/Users/span/Dropbox/Projects_Stanford/Neurochoice/Finance_project/fMRI_study/stock_analysis/stocks/data'
  stock_tc_dir <- '/Users/span/Dropbox/Projects_Stanford/Neurochoice/Finance_project/fMRI_study/stock_analysis/stocks/timecourses'
}

setwd(stock_data_dir)
df = read.csv('cleaned_wide_stock')
setwd(stock_tc_dir)

masks = c('nacc_desai_mpm', 'nacc8mm', 'acing', 'caudate', 'desai_ins', 'mpfc', 'demartino_dmpfc8mm')
sides = c('b') #,'l','r')

############ PLOT DATA ########
pd <- position_dodge(0.3)

for (side in sides) {
  for (mask in masks) {
    roi <- paste0(mask[1] ,side[1])
    d <-  filter(df, ROI == roi)

    ######## Stock Goes Up vs Down
    tt <- standard_title(side, mask,"Stock Outcome")
    plt <- standard_df(d, c('variable', 'Result'))
    cv = 'Result'
    fg <-  standard_fg(plt, cv)
    standard_save(plt, fg, tt, cv)
    # 
    
    ######## Stock Goes Up vs Down, Split by Previous Trial
    tt <- standard_title(side, mask,"Stock Outcome, Split by Previous Trial")
    plt <- standard_df(d, c('variable', 'Result', 'Previous_Trial'))
    cv = 'Result'
    fe <-  as.formula(". ~ Previous_Trial")
    fg <-  standard_fg(plt, cv, fe)
    standard_save(plt, fg, tt, cv)
    
    ######## Stock Goes Up vs Down, Split by Choice
    tt <- standard_title(side, mask,"Stock Goes Up vs Down, Split by Choice")
    plt <- standard_df(d, c('variable', 'Choice', 'Result'))
    fe <- as.formula(". ~ Choice")
    cv = 'Result'
    fg <-  standard_fg(plt, cv, fe)
    standard_save(plt, fg, tt, cv)
    
    ######## Buy vs Don't
    tt <- standard_title(side,mask, "Buy vs Don't")
    plt <- standard_df(d, c('variable', 'Choice'))
    cv = 'Choice'
    fg <-  standard_fg(plt,cv)
    standard_save(plt, fg, tt, cv)


    ######## Buy vs Don't, Split by Previous Trial
    tt <- standard_title(side, mask, "Buy vs Don't, Split by Previous Trial")
    plt <- standard_df(d, c('variable', 'Choice', 'Previous_Trial'))
    fe <- as.formula(". ~ Previous_Trial")
    cv = 'Choice'
    fg <-  standard_fg(plt, cv, fe)
    standard_save(plt, fg, tt, cv)

    ######## Buy vs Don't, Split by Previous Trial x Result
    tt <- standard_title(side, mask,"Buy vs Don't, Split by Previous Trial x Result")
    plt <- standard_df(d, c('variable', 'Choice', 'Previous_Trial', 'Result'))
    fe <- as.formula("Previous_Trial ~ Result")
    cv = 'Choice'
    fg <-  standard_fg(plt, cv, fe)
    standard_save(plt, fg, tt, cv)

  }
} 