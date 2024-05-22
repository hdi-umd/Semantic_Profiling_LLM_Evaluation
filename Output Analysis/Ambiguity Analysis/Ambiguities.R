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

gpt_df <- read_csv("../results/gpt_ambiguity_results.csv")
gemini_df <- read_csv("../results/gemini_ambiguity_results.csv")
llama_df <- read_csv("../results/llama_ambiguity_results.csv")
mistral_df <- read_csv("../results/mixtral_ambiguity_results.csv")

names(mistral_df)[names(mistral_df) == 'mixtral_query'] <- 'query'
names(gemini_df)[names(gemini_df) == 'gemini_query'] <- 'query'
names(llama_df)[names(llama_df) == 'llama_query'] <- 'query'
names(gpt_df)[names(gpt_df) == 'gpt_query'] <- 'query'


#starting analysis for relevant data column matches
columns_of_interest <- c("query","positive match", "llm match", "gt match", "resolution positive match", "resolution llm match", "resolution gt match", "ambiguity similarity match", "resolution similarity match")


gpt_col <- gpt_df[c("query","gpt_positive match", "gpt_llm match", "gpt_gt match", "gpt_resolution positive match", "gpt_resolution llm match", "gpt_resolution gt match", "gpt_ambiguity similarity match", "gpt_resolution similarity match")]
colnames(gpt_col)<- columns_of_interest
gpt_col["llm"] <- "GPT4"
rdc_df <- gpt_col

gemini_col <- gemini_df[c("query","gemini_positive match", "gemini_llm match", "gemini_gt match", "gemini_resolution positive match", "gemini_resolution llm match", "gemini_resolution gt match", "gemini_ambiguity similarity match", "gemini_resolution similarity match")]
colnames(gemini_col)<- columns_of_interest
gemini_col["llm"] <- "Gemini-Pro"
rdc_df <- rbind(rdc_df, gemini_col)

llama_col <- llama_df[c("query","llama_positive match", "llama_llm match", "llama_gt match", "llama_resolution positive match", "llama_resolution llm match", "llama_resolution gt match", "llama_ambiguity similarity match", "llama_resolution similarity match")]
colnames(llama_col)<- columns_of_interest
llama_col["llm"] <- "Llama3"
rdc_df <- rbind(rdc_df, llama_col)

mistral_col <- mistral_df[c("query","mixtral_positive match", "mixtral_llm match", "mixtral_gt match", "mixtral_resolution positive match", "mixtral_resolution llm match", "mixtral_resolution gt match", "mixtral_ambiguity similarity match", "mixtral_resolution similarity match")]
colnames(mistral_col)<- columns_of_interest
mistral_col["llm"] <- "Mixtral"
rdc_df <- rbind(rdc_df, mistral_col)

rdc_df <- as.data.frame(rdc_df)

#show total ambiguities for each llm
Total_found_by_gt <- rdc_df%>%
  filter(!is.na(`positive match`) | !is.na(`llm match`))%>%
  group_by(llm)%>%
  summarize(count=n())

rdc_df%>%
  group_by(llm)%>%
  summarize(
      non_na_match = sum(!is.na(`positive match`)) +sum(!is.na(`llm match`))
  )%>%
  ggplot(aes(x=non_na_match, y=llm))+
  geom_col(fill ="#69b3a2")+
  geom_text(aes(label = non_na_match), vjust = 0.5, color = "white")+
  theme_minimal()+
  theme(
    panel.background = element_blank(),axis.title.x=element_blank(),
    plot.title = element_text(hjust=0.5, vjust=-5),
  )+
  labs( y="", title = "")+
  guides(fill=guide_legend(nrow=1, reverse=TRUE))

#ambiguities found by both llm and gt
rdc_df%>%
  filter(!is.na(`positive match`) & !is.na(`resolution positive match`))%>%
  group_by(llm)%>%
  summarize(count=n())%>%
  ggplot(aes(x=count, y=llm))+
  geom_col(fill ="#69b3a2")+
  geom_text(aes(label = count), vjust = 1.6, color = "white")+
  theme_minimal()+
  theme(
    panel.background = element_blank(),axis.title.x=element_blank(),
    plot.title = element_text(hjust=0.5, vjust=-5),
  )+
  labs( y="", title = "")+
  guides(fill=guide_legend(nrow=1, reverse=TRUE))


#plot porportion of overlapping vs non overlapping ambiguities for each llm
rdc_df%>%
  mutate(
    agreements = ifelse(!is.na(`positive match`), "overlaps with gt", 
                        ifelse(!is.na(`llm match`), "llm only", 
                               ifelse(!is.na(`gt match`), "gt only", 
                                      NA
                              )
                      )
    )
  )%>%
  filter(!is.na(agreements))%>%
  mutate(agreements = fct_relevel(agreements,c("overlaps with gt","gt only","llm only")))%>%
  group_by(llm, agreements)%>%
  summarize(counts=n())%>%
  ggplot(aes(fill=agreements, y=llm, x=counts)) + 
  geom_bar(position="fill", stat="identity")+
  scale_x_continuous(labels = percent)+
  scale_fill_manual(
    labels = c("LLM + HM", "HM Only", "LLM Only"), 
    values = c("#E59D23", "#8B8500", "#006B60")
  )+
  theme_minimal()+
  theme(
    text = element_text(size=15),
    aspect.ratio = 1/4, legend.position = c(.5,-.45),
    # panel.background = element_blank(),axis.title.x=element_blank(),
    plot.title = element_text(hjust=0.2),
    legend.direction = "horizontal"
  )+
  labs( x="% of responses", y="",
        title = "Overlapping Uncertainty Annotations")+
  guides(fill=guide_legend(title = "", title.position = "left"))


rdc_df%>%
  filter(!is.na(`ambiguity similarity match`) & !is.na(`resolution similarity match`))%>%
  pivot_longer(cols=c("ambiguity similarity match", "resolution similarity match"),
               names_to = "metric",
               values_to = "values")%>%
  ggplot(aes(x=metric, y=values, fill=llm))+
  geom_boxplot()+
  scale_fill_manual(
    # labels = c("LLM + HM", "HM Only", "LLM Only"), 
    # values = c("#E59D23", "#6F3A00", "#006B60", "#62BAAD")
    values = c("#00ADB4", "#00545C", "#A63B00", "#FF8945")
  )+
  scale_x_discrete(labels=c("Ambiguity Description", "Resolution Description"))+
  theme_minimal()+
  theme(
    aspect.ratio = 1/2, legend.position = c(.5,-.1),
    panel.background = element_blank(),axis.title.x=element_blank(),
    plot.title = element_text(hjust=0.5),
  )+
  labs( y="Cosine Similarity Score", 
        title = "Similarity Scores for Ambiguity Descriptions")+
  guides(fill=guide_legend(nrow=1,title = ""))


rdc_df%>%
  group_by(llm)%>%
  filter(!is.na(`ambiguity similarity match`))%>%
  summarize(avg_sim = mean(`ambiguity similarity match`))

mean(rdc_df[["ambiguity similarity match"]], na.rm=T)
sd(rdc_df[["ambiguity similarity match"]], na.rm=T)
