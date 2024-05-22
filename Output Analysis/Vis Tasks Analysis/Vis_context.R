#set working dir to current file dir
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

#import libaries
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

gpt_df <- read_csv("./results/gpt_vis_context_results.csv")
gemini_df <- read_csv("./results/gemini_vis_context_results.csv")
llama_df <- read_csv("./results/llama_vis_context_results.csv")
mistral_df <- read_csv("./results/mixtral_vis_context_results.csv")

names(mistral_df)[names(mistral_df) == 'mixtral_query'] <- 'query'
names(gemini_df)[names(gemini_df) == 'gemini_query'] <- 'query'
names(llama_df)[names(llama_df) == 'llama_query'] <- 'query'
names(gpt_df)[names(gpt_df) == 'gpt_query'] <- 'query'

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
mistral_col["llm"] <- "Mixtral"
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


#looks like theres high disagreement between llm and gt for vis context
rdc_df%>%
  mutate(
    agreements = ifelse(`positive matches count`>0 & (`llm only matches count`==0 & `gt only matches count`==0), "agreement", 
                        ifelse(`positive matches count`==0 & (`llm only matches count`>0 & `gt only matches count`>0), "disagreement", 
                               "partial-agreement"
                        )
                )
  )%>%
  mutate(agreements = fct_relevel(agreements,c("agreement","partial-agreement","disagreement")))%>%
  filter(!is.na(agreements))%>%
  group_by(llm, agreements)%>%
  summarize(
    counts=n(),
    percentage = n()/ nrow(rdc_df) * 100
    )%>%
  ggplot(aes(fill=agreements, y=llm, x=counts)) + 
  geom_bar(position="fill", stat="identity")+
  scale_x_continuous(labels = percent)+
  scale_fill_manual(
    labels = c("Total agreeement", "Partial Agreement", "Total disagreement"), 
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
  labs( x="% of responses", y="", title ="LLM and Human Visual Task Annotations")+
guides(fill=guide_legend(title = ""))

#starting analysis for vis goal matches
columns_of_interest <- c("query","correct goal classifications", "missing goal classifications")


gpt_col <- gpt_df[c("query", "gpt_correct goal classifications", "gpt_missing goal classifications")]
colnames(gpt_col)<- columns_of_interest
gpt_col["llm"] <- "GPT4"
rdc_df <- gpt_col

gemini_col <- gemini_df[c("query", "gemini_correct goal classifications", "gemini_missing goal classifications")]
colnames(gemini_col)<- columns_of_interest
gemini_col["llm"] <- "Gemini-Pro"
rdc_df <- rbind(rdc_df, gemini_col)

llama_col <- llama_df[c("query", "llama_correct goal classifications", "llama_missing goal classifications")]
colnames(llama_col)<- columns_of_interest
llama_col["llm"] <- "Llama3"
rdc_df <- rbind(rdc_df, llama_col)

mistral_col <- mistral_df[c("query", "mixtral_correct goal classifications", "mixtral_missing goal classifications")]
colnames(mistral_col)<- columns_of_interest
mistral_col["llm"] <- "Mixtral"
rdc_df <- rbind(rdc_df, mistral_col)

#correct classifications
rdc_df%>%
  filter(!is.na(`correct goal classifications`))%>%
  group_by(llm, `correct goal classifications`)%>%
  summarize(
    counts=n(),
    percentage = n()/ nrow(rdc_df) *100
    )%>%
  ggplot(aes(fill=`correct goal classifications`, y=llm, x=counts)) + 
  geom_bar(position="fill", stat="identity")+
  scale_x_continuous(labels = percent)+
  scale_fill_manual(
    labels = c("Agreement", "Disagreement"), 
    values = c("#E59D23", "#006B60")
    )+
  theme_minimal()+
  theme(
    aspect.ratio = 1/4, legend.position = c(.5,-.45),
    # panel.background = element_blank(),axis.title.x=element_blank(),
    plot.title = element_text(hjust=0.2),
    legend.direction = "horizontal"
  )+
  labs( x="% of responses", y="",
        title = "Agreement Between LLM and Human Annotations for Visual Goal")+
  guides(fill=guide_legend(title = ""))
