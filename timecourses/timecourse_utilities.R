# WIDE format timecourse utilities. 
library(dplyr)
library(reshape2)
library(ggplot2)
######### Helper Functions Stolen from the Internet ##########

simpleCap <- function(x) {
  ## Simple capitalization function
  s <- strsplit(x, " ")[[1]]
  paste(toupper(substring(s, 1,1)), substring(s, 2),
        sep="", collapse=" ")
}


summarySE <- function(data=NULL, measurevar, groupvars=NULL, na.rm=FALSE,
                      conf.interval=.95, .drop=TRUE) {
  ##   Gives count, mean, standard deviation, standard error of the mean, and confidence interval (default 95%).
  ##   data: a data frame.
  ##   measurevar: the name of a column that contains the variable to be summariezed
  ##   groupvars: a vector containing names of columns that contain grouping variables
  ##   na.rm: a boolean that indicates whether to ignore NA's
  ##   conf.interval: the percent range of the confidence interval (default is 95%)
  
  # New version of length which can handle NA's: if na.rm==T, don't count them
  length2 <- function (x, na.rm=TRUE) {
    if (na.rm) sum(!is.na(x))
    else       length(x)
  }
  
  # This does the summary. For each group's data frame, return a vector with
  # N, mean, and sd
  datac <- plyr::ddply(data, groupvars, .drop=.drop,
                 .fun = function(xx, col) {
                   c(N    = length2(xx[[col]], na.rm=na.rm),
                     mean = mean   (xx[[col]], na.rm=na.rm),
                     sd   = sd     (xx[[col]], na.rm=na.rm)
                   )
                 },
                 measurevar
  )
  
  # Rename the "mean" column    
  datac <- plyr::rename(datac, c("mean" = measurevar))
  
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

standard_df <- function(df, roi, grouping_vars=NULL, max_tr = 15) {
  #get rid of all the trs that aren't for the roi we want
  is.tr <- sapply(colnames(df), function(x) grepl('_TR_',x))
  print(is.tr)
  is.not.right <-  sapply(colnames(df), function(x) !grepl(roi,x))
  keep <- !(is.tr & is.not.right)
  plt <- summarySE(melt(df[,keep]), measurevar="value", groupvars= grouping_vars, na.rm = TRUE)
  plt <- plt[sapply(plt$variable, function(x) grepl('_TR_',x)),]
  plt$time <- 2 * (as.numeric(sapply(plt$variable, function(x) sub(paste0(roi, '_TR_'), '',x))) - 1)
  plt <- dplyr::filter(plt, time<=max_tr*2)
  plt
}

standard_fg <- function(plt, color_var, fe=NULL) {
  fg <- ggplot(plt, aes_string(x='time', y='value', colour=color_var)) +
    geom_errorbar(aes(ymin=value-se, ymax=value+se), width=.5, position=pd) +
    geom_line(position=pd, aes_string(group=color_var,color=color_var)) +
    geom_point(position=pd, size=2, shape=21, fill="white") + # 21 is filled circle
    xlab("Seconds") +
    ylab("%\u0394 BOLD") +
    scale_y_continuous(breaks=-10:10*mean(plt$value)) +
    scale_x_continuous(breaks=c(seq(2,32, by=2))) +
    theme(axis.text.x = element_text(angle = 45, hjust = 1)) + 
    scale_fill_manual(values=c("#E69F00", "#56B4E9", "#D55E00", "#CC79A7",  "#F0E442", "#009E73", "#0072B2")) + 
    scale_color_manual(values=c("#E69F00", "#56B4E9", "#D55E00", "#CC79A7",  "#F0E442", "#009E73", "#0072B2"))
    
  if (!is.null(fe)) {
    fg <- fg + facet_grid(fe, scales="free")
  }
  fg
}

bw_fg <- function(plt, color_var, fe=NULL, max_tr=15, legend, legend_title) {
  fg <- ggplot(plt, aes_string(x='time', y='value', colour=color_var, linetype=color_var)) +
    geom_errorbar(aes(ymin=value-se, ymax=value+se), width=.6, position=pd) + # plot SEM
    geom_line(position=pd, aes_string(group=color_var,color=color_var), size=2.5) +
    geom_point(position=pd, aes_string(group=color_var,fill=color_var), size=8, shape=21, stroke = 3) + # 21 is filled circle
    xlab("Seconds") +
    ylab("% Signal Change") +
    #ylim(-0.1, 0.1) + # Use this if you want to fix y-axes
    scale_y_continuous(breaks=-10:10*.1) +
    scale_x_continuous(breaks=c(seq(0,max_tr*2, by=2))) +
    scale_fill_manual(values=c('black','white'), labels = legend, name = legend_title)+
    theme(text=element_text(family='Helvetica', size=24, colour = 'black'),
          axis.text=element_text(family='Helvetica', size=24, colour = 'black'),
          axis.line = element_line(linetype = "solid", size = 2, colour = "black"),
          legend.justification=c(0,1), legend.position='right', #
          legend.key.size=unit(1,units = 'cm'),
          legend.text = element_text(size = 16, family = "Helvetica"),
          panel.grid.minor= element_line(color = "black", linetype = "dotted"),
          panel.grid.major= element_line(color = "black", linetype = "dotted", size = 0.5),
          panel.background = element_blank(),
          panel.border = element_rect(colour = "black", fill=NA, size=3))+
    scale_colour_manual(values = c("black","gray41"), labels = legend, name = legend_title)+
    scale_linetype_manual(values=c('solid','solid'),  labels = legend, name = legend_title)+
    annotate("rect", xmin=-Inf,xmax=5,ymin=-Inf,ymax=Inf,alpha=0.5, fill = "gray50")+ # To get TR_3: xmax = 3, TR_4: xmax = 5
    annotate("rect", xmin=7,xmax=Inf,ymin=-Inf,ymax=Inf,alpha=0.5, fill = "gray50") # To get TR_3: xmin = 5, TR_4: xmax = 7
   # geom_vline(xintercept = c(5,7,11,13), linetype = "dashed", size=1.5) # set x-coordinates for vertical lines 
    if (!is.null(fe)) {
    fg <- fg + facet_grid(fe, scales="free")+
      theme(strip.text.x = element_text(size = 24, family = "Helvetica"))
  }
  fg
}

standard_title <- function(side, mask, ts, exp) {
  bar_title = do.call(paste,as.list(sapply(c(side,mask, "\u0394 BOLD", ts, "- Bars", "- Exp", exp),simpleCap)))
  band_title = do.call(paste,as.list(sapply(c(side,mask, "\u0394 BOLD", ts, "- Bands", "- Exp", exp),simpleCap)))
  list('bar' = bar_title, 'band' = band_title)
}


standard_save <- function(plt, fg, tt, cv, wid=30, hgt=12) {
  #save bar
  fg <- fg + ggtitle(tt$bar)
   ggsave(file=paste0(tt$bar,'.png'), width = wid, height=hgt)
  
  #save band
  fg <- fg + geom_ribbon(data=plt, aes_string(ymin='value-se', ymax='value+se', alpha='.5',fill=cv), position=pd)
  fg <- fg + ggtitle(tt$band)
  ggsave(file=paste0(tt$band,'.png'), width = 24, height=8)
}
