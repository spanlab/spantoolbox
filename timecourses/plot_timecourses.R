library(ggplot2)
source('timecourse_utilities.R')
df = read.csv('../voi/voi_csv/merged_voi_augmented_tr.csv')

masks = c( 'nacc8mm', 'desai_ins', 'mpfc')
sides = c('b') #,'l','r')

############ PLOT DATA ########
pd <- position_dodge(0.3)

for (exp in c("1","2")) {
    tc_dir <- paste0('stock_', exp)
    setwd(tc_dir)
    
    for (side in sides) {
      for (mask in masks) {
        roi <- paste0(mask[1] ,side[1])

        subdf <- dplyr::filter(df, Experiment==as.integer(exp))
        max_tr = 8 # Change this number to set the TRs on the x-axis (times 2)
        ######## Stock Goes Up vs Down, Split by Previous Trial
        tt <- standard_title(side, mask,"Stock Outcome, Split by Previous Trial", exp)
        plt <- standard_df(subdf, roi, c('variable', 'Result', 'Previous_Trial'), max_tr=max_tr)
        write.csv(x=plt, paste0(mask, side,'_', exp, '_stock_outcome_split_trial.csv'))
        print(nrow(df))
        print(nrow(plt))
        color_by = 'Result'
        facet_eqn <-  as.formula(". ~ Previous_Trial")
        legend_title <- "Next Day:"
        legend <- c("Down", "Up")
        fg <-  bw_fg(plt, color_by, facet_eqn, max_tr = max_tr, legend=legend , legend_title=legend_title)
        labels <- c("Went Down" = "Previous day: Price went DOWN", "Went Up" = "Previous day: Price went UP")
        fg <- fg + facet_grid(facet_eqn, labeller=labeller(Previous_Trial = labels))
        standard_save(plt, fg, tt, color_by)

        ######## Buy vs Don't, Split by Previous Trial
        tt <- standard_title(side, mask, "Buy vs Don't, Split by Previous Trial", exp)
        plt <- standard_df(subdf, roi, c('variable', 'Choice', 'Previous_Trial'), max_tr=max_tr)
        write.csv(x=plt, paste0(mask, side,'_', exp, 'buy_vs_not_by_previous_trial.csv'))
        color_by = 'Choice'
        facet_eqn <- as.formula(". ~ Previous_Trial")
        legend_title <- "Choice"
        legend <- c("No", "Yes")
        fg <-  bw_fg(plt, color_by, facet_eqn, max_tr = max_tr, legend=legend , legend_title=legend_title)
        labels <- c("Went Down" = "Price Went Down", "Went Up" = "Price Went Up")
        fg <- fg + facet_grid(facet_eqn, labeller=labeller(Previous_Trial = labels))
        standard_save(plt, fg, tt, color_by)

        ####### Buy vs Don't - Note that for simple graphs 'facet_eqn' is removed in fg <- bw_fg() as we don't split by another variable
        ## To play with white background selection: change xmin and xmax in function bw_fg above
        tt <- standard_title(side, mask,"Buy vs Don't", exp)
        plt <- standard_df(subdf, roi, c('variable', 'Choice'), max_tr=max_tr)
        write.csv(x=plt, paste0(mask, side,'_', exp, 'buy_vs_not.csv'))
        color_by = 'Choice'
        legend_title <- "Choice"
        legend <- c("No", "Yes")
        fg <-  bw_fg(plt, color_by, max_tr = max_tr, legend=legend , legend_title=legend_title)
        standard_save(plt, fg, tt, color_by)

        ######## Stock Goes Up vs Down
        tt <- standard_title(side, mask,"Stock Outcome", exp)
        plt <- standard_df(subdf, roi, c('variable', 'Result'), max_tr=max_tr)
        write.csv(x=plt, paste0(mask, side,'_', exp, 'stock_outcome.csv'))
        color_by = 'Result'
        legend_title <- "Next Day:"
        legend <- c("Down", "Up")
        fg <-  bw_fg(plt, color_by, max_tr = max_tr, legend=legend , legend_title=legend_title)
        standard_save(plt, fg, tt, color_by)

        ######## Buy vs not
        tt <- standard_title(side, mask,"Buy Vs Not", exp)
        plt <- standard_df(subdf, roi, c('variable', 'Choice'), max_tr=max_tr)
        write.csv(x=plt, paste0(mask, side,'_', exp, 'buy_vs_not.csv'))
        color_by = 'Choice'
        legend_title <- "Choice"
        legend <- c("Don't Buy", "Buy")
        fg <-  bw_fg(plt, color_by, max_tr = max_tr, legend=legend , legend_title=legend_title)
        standard_save(plt, fg, tt, color_by)

      }

    } 
    setwd('..')
}