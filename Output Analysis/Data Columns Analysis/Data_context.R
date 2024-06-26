#set working dir to current file dir
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

#import libaries
library(dplyr)
library(car)
library(tidyr)
library(ggplot2)
library(gridExtra)
library(tidyverse)
library(viridis)
library(ggstatsplot)
library("coin")
library("rstatix")
library(hrbrthemes)
library(nlme)
library(lme4)
library(scales)
library(report)
library(ggpattern)

gpt_df <- read_csv("./results/gpt_data_context_results.csv")
gemini_df <- read_csv("./results/gemini_data_context_results.csv")
llama_df <- read_csv("./results/llama_data_context_results.csv")
mistral_df <- read_csv("./results/mixtral_data_context_results.csv")


names(mistral_df)[names(mistral_df) == 'mixtral_query'] <- 'query'
names(gemini_df)[names(gemini_df) == 'gemini_query'] <- 'query'
names(llama_df)[names(llama_df) == 'llama_query'] <- 'query'
names(gpt_df)[names(gpt_df) == 'gpt_query'] <- 'query'

get_column<-function(name, df){
  return(df[, grepl( name , names( df ) ) ])
}

#starting analysis for relevant data column matches
columns_of_interest <- c("query","positive matches count", "llm only matches count", "gt only matches count")


gpt_col <- gpt_df[c("query", "gpt_positive matches count", "gpt_llm only matches count", "gpt_gt only matches count")]
colnames(gpt_col)<- columns_of_interest
gpt_col["llm"] <- "GPT4"
rdc_df <- gpt_col

gemini_col <- gemini_df[c("query", "gemini_positive matches count", "gemini_llm only matches count", "gemini_gt only matches count")]
colnames(gemini_col)<- columns_of_interest
gemini_col["llm"] <- "Gemini-Pro"
rdc_df <- rbind(rdc_df, gemini_col)

llama_col <- llama_df[c("query", "llama_positive matches count", "llama_llm only matches count", "llama_gt only matches count")]
colnames(llama_col)<- columns_of_interest
llama_col["llm"] <- "Llama3"
rdc_df <- rbind(rdc_df, llama_col)

mistral_col <- mistral_df[c("query", "mixtral_positive matches count", "mixtral_llm only matches count", "mixtral_gt only matches count")]
colnames(mistral_col)<- columns_of_interest
mistral_col["llm"] <- "Mistral"
rdc_df <- rbind(rdc_df, mistral_col)

# total prompts processed for each llm
rdc_df <- as.data.frame(rdc_df)
rdc_df%>%
  group_by(llm)%>%
  summarize(count=n())%>%
  ggplot(aes(x=llm, y=count))+
  geom_col(fill ="#69b3a2")+
  geom_text(aes(label = count), vjust = 1.6, color = "white")+
  theme_minimal()+
  theme(
    panel.background = element_blank(),axis.title.x=element_blank(),
    plot.title = element_text(hjust=0.5, vjust=-5),
  )+
  labs( y="", title = "")+
  guides(fill=guide_legend(nrow=1, reverse=TRUE))

#14 cases where the groundtruths did not find any data columns but llms returned something. Interesting to look at because these might be situations where the llm 
# outperformed our human judgement at making inferrences.
no_gt_dc <- rdc_df%>%
  filter(`positive matches count`==0 & `gt only matches count`==0)
no_gt <- unique(no_gt_dc$query)

rdc_df<- rdc_df[! rdc_df$query %in% no_gt,]

#for all propmpts what level of agreement did we get between the llm and gt?
rdc_df<-rdc_df%>% 
  filter(!is.na(`positive matches count`)&!is.na(`llm only matches count`) & !is.na(`gt only matches count`))%>%
  mutate(
    agreements = ifelse(`positive matches count`>0 & (`llm only matches count`==0 & `gt only matches count`==0), "Total agreement", 
                        ifelse(`positive matches count`==0 & (`llm only matches count`>0 & `gt only matches count`>0), "Total disagreement", 
                               "Partial agreement"
                        )
    )
  )%>%
  mutate(agreements = fct_relevel(agreements,c("Total agreement","Partial agreement","Total disagreement")))

nrow(rdc_df)
  
vis_df <- rdc_df%>%
  filter(!is.na(agreements))%>%
  group_by(llm, agreements)%>%
  summarize(
    counts=n(),
    percentage = n()/ nrow(rdc_df) * 100
    )

vis_df%>%
  ggplot(aes(fill=agreements, y=llm, x=counts)) + 
  geom_bar(position="fill", stat="identity")+
  scale_x_continuous(labels = percent)+
  scale_y_discrete(labels=c("Gemini-Pro", "GPT-4", "Llama3", "Mixtral"))+
  scale_fill_manual(
    labels = c("Total agreeement", "Partial agreement", "Total disagreement"), 
    values = c("#E59D23", "#8B8500", "#006B60")
  )+
  theme_minimal()+
  theme(
    aspect.ratio = 1/4, legend.position = c(.5,-.45),
    # panel.background = element_blank(),axis.title.x=element_blank(),
    plot.title = element_text(hjust=0.2),
    text = element_text(size=15),
    legend.direction = "horizontal"
  )+
  labs( x="% of responses", y="", title = "LLM and Human Data Column Annotations")+
  guides(fill=guide_legend(title = ""))

# Pattern based chart for accessibility purposes
vis_df%>%
  ggplot(aes(y=llm, x=counts)) + 
  geom_bar_pattern(
    aes(
      pattern_fill = agreements,
      pattern = agreements,
      fill= agreements
    ),  
    position = "fill",
    stat="identity",
    colour  = 'black',
    # fill = "white",
    pattern_density = 0.5,
    pattern_key_scale_factor = 0.2
  )+
  scale_x_continuous(labels = percent)+
  scale_pattern_fill_manual(
    # labels = c("Total agreement", "Partial Agreement", "Total disagreement"),
    values = c("Total agreement"="#E59D23", "Partial agreement"="#8B8500", "Total disagreement"="#006B60")
  )+
  scale_fill_manual(
    # labels = c("Total agreeement", "Partial Agreement", "Total disagreement"),
    values = c("#E59D23", "#8B8500", "#006B60"),
    # values= cbPalette,
    guide="none"
  )+
  theme_minimal()+
  theme(
    aspect.ratio = 1/4, legend.position = c(.5,-.45),
    # panel.background = element_blank(),axis.title.x=element_blank(),
    plot.title = element_text(hjust=0.3),
    text = element_text(size=20),
    legend.direction = "horizontal",
    legend.title=element_blank()
  )+
  labs( x="% of responses", y="", title ="LLM and Human Data Column Annotations")


# in the cases where the column was not found by llm, what \% of them were because they were inferred?

#data transforms
dt_trans <- read_csv("./results/cleaned_transforms_results.csv")
dt_trans["total_examined"] <- dt_trans["errors_count"] + dt_trans["non_df_returned_count"] + dt_trans["total_dfs_returned"]

dt_trans%>%
  pivot_longer(
    cols=c("errors_count", "non_df_returned_count","total_dfs_returned"),
    names_to = "metrics",
    values_to = "count"
  )%>%
  ggplot(aes(fill=metrics, y=count, x=llm)) + 
  geom_bar(position="fill", stat="identity")


dt_trans%>%
  pivot_longer(
    cols=c("matching_df", "mismatching_df"),
    names_to = "metrics",
    values_to = "count"
  )%>%
  mutate(metrics = fct_relevel(metrics,c("matching_df", "mismatching_df")))%>%
  ggplot(aes(fill=metrics, y=llm, x=count)) + 
  geom_bar(position="fill", stat="identity")+
  scale_x_continuous(labels = percent)+
  scale_y_discrete(labels=c("Gemini-Pro", "GPT-4", "Llama3", "Mixtral"))+
  scale_fill_manual(
    labels = c("Matching data schemas", "Mismatched data schemas"), 
    values = c("#E59D23","#8B8500","#006B60")
  )+
  theme_minimal()+
  theme(
    aspect.ratio = 1/4, legend.position = c(.5,-.45),
    # panel.background = element_blank(),axis.title.x=element_blank(),
    plot.title = element_text(hjust=0.2),
    text = element_text(size=15),
    legend.direction = "horizontal"
  )+
  labs( x="% of responses", y="", title = "LLMs vs Human Annotations Schema Matches")+
  guides(fill=guide_legend(title = ""))

#pattern based chart for accessibility
out<-rename(dt_trans, c("matching_df" = "Matching data schemas", "mismatching_df" = "Mismatched data schemas"))
dt_trans%>%
  pivot_longer(
    cols=c("matching_df", "mismatching_df"),
    names_to = "metrics",
    values_to = "count"
  )%>%
  mutate(metrics = fct_relevel(metrics,c("matching_df", "mismatching_df")))%>%
  ggplot(aes(y=llm, x=count)) + 
  geom_bar_pattern(
    aes(
      pattern_fill = metrics,
      pattern = metrics
      # fill= metrics
    ),  
    position = "fill",
    stat="identity",
    colour  = 'black',
    fill = "white",
    pattern_density = 0.5,
    pattern_key_scale_factor = 0.2
  )+
  scale_x_continuous(labels = percent)+
  scale_pattern_fill_manual(
    # labels = c("Matching data schemas", "Mismatched data schemas"),
    values = c("matching_df"="#E59D23", "mismatching_df"="#8B8500")
  )+
  # scale_fill_manual(
  #   values = c("#E59D23", "#8B8500", "#006B60"),
  #   # values= cbPalette,
  #   guide="none"
  # )+
  theme_minimal()+
  theme(
    aspect.ratio = 1/4, legend.position = c(.5,-.45),
    # panel.background = element_blank(),axis.title.x=element_blank(),
    plot.title = element_text(hjust=0.3),
    text = element_text(size=20),
    legend.direction = "horizontal",
    legend.title=element_blank()
  )+
  labs( x="% of responses", y="", title = "LLMs vs Human Annotations Schema Matches")
  # guides(fill=guide_legend(title = ""))


#how many of the disagreements had ambiguities?
ambiguity <- read_csv("../results/gpt_ambiguity_results.csv")
disagreements <- rdc_df[rdc_df$agreements == "disagreement",]
udis<- unique(disagreements$query)
ambi <-  ambiguity[ambiguity$gpt_query%in%udis,]

