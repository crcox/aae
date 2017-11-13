library('dplyr')
library('ggplot2')

ACCENT.mean <- ACCENT %>%
  group_by(epoch,condition,dialect,accent,teston,input,output) %>%
  summarize(ss_se = sd(sensspec)/sqrt(n), sensspec=mean(sensspec), error=mean(error), se=sd(error)/sqrt(n)) %>% ungroup

ACCENT.cepoch <- ACCENT.mean %>%
  group_by(condition,dialect,accent) %>%
  summarize(
    e05=epoch[match(TRUE,error<0.05)],
    e10=epoch[match(TRUE,error<0.10)],
    e15=epoch[match(TRUE,error<0.15)],
    e20=epoch[match(TRUE,error<0.20)]) %>% ungroup()

DIALECT.mean <- DIALECT %>%
  group_by(epoch,condition,dialect,accent,teston,input,output) %>%
  summarize(ss_se = sd(sensspec)/sqrt(n), sensspec=mean(sensspec), error=mean(error), se=sd(error)/sqrt(n)) %>% ungroup

DIALECT.cepoch <- DIALECT.mean %>%
  group_by(condition,dialect,accent) %>%
  summarize(
    e05=epoch[match(TRUE,error<0.05)],
    e10=epoch[match(TRUE,error<0.10)],
    e15=epoch[match(TRUE,error<0.15)],
    e20=epoch[match(TRUE,error<0.20)]) %>% ungroup()

ggplot(filter(DIALECT.mean,condition=="Blocked"), aes(x=epoch, y=error, color=teston))+ geom_line() + facet_grid(input~output) + ggtitle("Blocked dialect training") + theme_grey(base_size = 24)
ggplot(filter(DIALECT.mean,condition=="Interleaved"), aes(x=epoch, y=error, color=teston))+ geom_line() + facet_grid(input~output) + ggtitle("Interleaved dialect training") + theme_grey(base_size = 24)

ggplot(filter(ACCENT.mean,condition=="Blocked_accent",dialect=="AAE",epoch<100), aes(x=epoch, y=error, color=teston))+ geom_line() + facet_grid(input~output) + ggtitle("Blocked accent training (AAE)") + theme_grey(base_size = 24)
ggplot(filter(ACCENT.mean,condition=="Interleaved_accent", dialect=="AAE",epoch<100), aes(x=epoch, y=error, color=teston))+ geom_line() + facet_grid(input~output) + ggtitle("Interleaved accent training (AAE)") + theme_grey(base_size = 24)
ggplot(filter(ACCENT.mean,condition=="Blocked_accent", dialect=="SAE",epoch<100), aes(x=epoch, y=error, color=teston))+ geom_line() + facet_grid(input~output) + ggtitle("Blocked accent training (SAE)") + theme_grey(base_size = 24)
ggplot(filter(ACCENT.mean,condition=="Interleaved_accent", dialect=="SAE",epoch<100), aes(x=epoch, y=error, color=teston))+ geom_line() + facet_grid(input~output) + ggtitle("Interleaved accent training (SAE)") + theme_grey(base_size = 24)
