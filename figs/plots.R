# Data plots for the course pages (fictional example data).
#
#   module load R/4.6.1
#   Rscript figs/plots.R          # run from the repo root
#
# W4: three "avoid vs choose" graph comparisons, Korean (*.svg) and English (*.en.svg) titles.
# W5: a mock Figure 2 that the legend before/after example describes.
# All numbers come from the fictional example study used across the course:
#   fibrotic area sham 1.9 ± 0.6, UUO + vehicle 18.2 ± 4.0, UUO + compound X 9.6 ± 3.1 (%, mean ± SD, n = 6)
#   MF2 share of fibroblasts: median 24% (fibrosis, 8 patients) vs 7% (control, 6 patients), Wilcoxon P = 0.008
# Colours: slide-gallery charcoal palette; compound X / fibrosis in the slate blue pair colour.

suppressPackageStartupMessages({ library(ggplot2); library(patchwork); library(dplyr); library(tidyr) })

INK <- "#2F343B"; GREY1 <- "#ACAEB1"; GREY2 <- "#787B80"; KEY <- "#3F6A92"; AVOID <- "#E5484D"
FAM <- "Pretendard"
theme_web <- function(base = 10) {
  theme_classic(base_size = base, base_family = FAM) +
    theme(axis.text = element_text(colour = INK), axis.title = element_text(colour = INK),
          axis.line = element_line(linewidth = 0.3, colour = INK), axis.ticks = element_line(linewidth = 0.3, colour = INK),
          plot.title = element_text(size = base + 0.5, face = "bold", colour = INK, margin = margin(b = 6)),
          plot.title.position = "plot", strip.background = element_blank(),
          strip.text = element_text(colour = INK, face = "bold"), legend.position = "none",
          plot.margin = margin(6, 10, 6, 6))
}
theme_set(theme_web())
avoid_title <- function(p) p + theme(plot.title = element_text(colour = AVOID))

exact <- function(n, m, s, seed) { set.seed(seed); x <- rnorm(n); m + s * (x - mean(x)) / sd(x) }
GROUPS <- c("sham", "UUO + vehicle", "UUO + compound X")
fib <- tibble(group = factor(rep(GROUPS, each = 6), levels = GROUPS),
              area = c(exact(6, 1.9, 0.6, 1), exact(6, 18.2, 4.0, 2), exact(6, 9.6, 3.1, 3)))
GCOL <- setNames(c(GREY1, GREY2, KEY), GROUPS)

TXT <- list(
  ko = list(a1 = "피할 것: 평균만 보이는 막대", a2 = "고를 그래프: 표본별 점과 평균 ± SD",
            b1 = "피할 것: 세포를 n으로 센 P 값", b2 = "고를 그래프: 환자별 값으로 검정",
            c1 = "피할 것: 원그래프", c2 = "고를 그래프: 환자별 누적 막대"),
  en = list(a1 = "Avoid: bars that show only the mean", a2 = "Choose: every sample, mean ± SD",
            b1 = "Avoid: P value with cells as n", b2 = "Choose: test on patient values",
            c1 = "Avoid: pie charts", c2 = "Choose: a stacked bar per patient"))

out <- function(week, name, lang) file.path("assets", "img", week, paste0(name, if (lang == "en") ".en" else "", ".svg"))
fmtp <- function(p) if (p < 1e-4) "P < 0.0001" else sprintf("P = %.4f", p)

# ---- W4-1: few samples per group ---------------------------------------------------------
summ <- fib |> group_by(group) |> summarise(m = mean(area), s = sd(area), se = s / sqrt(n()), .groups = "drop")
ylab_fib <- "Fibrotic area (%)"
p_bar <- ggplot(summ, aes(group, m, fill = group)) + geom_col(width = 0.6) +
  geom_errorbar(aes(ymin = m, ymax = m + se), width = 0.2, linewidth = 0.3) +
  scale_fill_manual(values = GCOL) + scale_y_continuous(limits = c(0, 26), expand = c(0, 0)) +
  scale_x_discrete(labels = function(x) sub(" \\+ ", "\n+ ", x)) + labs(x = NULL, y = ylab_fib)
p_dot <- ggplot(fib, aes(group, area, colour = group)) +
  geom_point(position = position_jitter(width = 0.12, seed = 4), size = 2.2) +
  stat_summary(fun = mean, geom = "crossbar", width = 0.45, linewidth = 0.3, colour = INK) +
  stat_summary(fun.data = mean_sdl, fun.args = list(mult = 1), geom = "errorbar", width = 0.18, linewidth = 0.3, colour = INK) +
  scale_colour_manual(values = GCOL) + scale_y_continuous(limits = c(0, 26), expand = c(0, 0)) +
  scale_x_discrete(labels = function(x) sub(" \\+ ", "\n+ ", x)) + labs(x = NULL, y = ylab_fib)

# ---- W4-2: cells as n (pseudoreplication) ------------------------------------------------
# Patient means differ little (patient-level P is not significant), but thousands of cells make
# a cell-level test look overwhelming. Seed chosen so the two P values show this clearly.
set.seed(18)
mu <- c(rnorm(8, 1.25, 0.32), rnorm(6, 1.05, 0.32))
ncell <- sample(150:300, 14, replace = TRUE)
vals <- mapply(function(m, k) rnorm(k, m, 0.9), mu, ncell, SIMPLIFY = FALSE)
pts <- tibble(patient = c(paste0("F", 1:8), paste0("C", 1:6)),
              condition = factor(c(rep("Fibrosis", 8), rep("Control", 6)), levels = c("Control", "Fibrosis")))
cells <- pts |> mutate(value = vals) |> unnest(value)
pt_means <- cells |> group_by(patient, condition) |> summarise(value = mean(value), .groups = "drop")
p_cell <- wilcox.test(value ~ condition, data = cells)$p.value
p_pat <- wilcox.test(value ~ condition, data = pt_means, exact = TRUE)$p.value
CCOL <- c(Control = GREY1, Fibrosis = KEY)
ylab_acta2 <- "Acta2 in fibroblasts\n(log-normalized)"
base_violin <- ggplot(cells, aes(condition, value, fill = condition)) +
  geom_violin(scale = "width", width = 0.7, linewidth = 0.2, colour = NA, alpha = 0.45) +
  scale_fill_manual(values = CCOL) + scale_colour_manual(values = CCOL) +
  coord_cartesian(ylim = c(-2, 4.6)) + labs(x = NULL, y = ylab_acta2)
p_v_bad <- base_violin + geom_boxplot(width = 0.12, outlier.shape = NA, linewidth = 0.25, fill = "white") +
  annotate("text", x = 1.5, y = 4.4, family = FAM, size = 3.4, colour = INK,
           label = sprintf("Wilcoxon on %s cells\nP < 1e-%d", format(nrow(cells), big.mark = ","), floor(-log10(p_cell))))
p_v_good <- base_violin + geom_point(data = pt_means, aes(condition, value, colour = condition),
                                     position = position_jitter(width = 0.08, seed = 5), size = 2.4, inherit.aes = FALSE) +
  annotate("text", x = 1.5, y = 4.4, family = FAM, size = 3.4, colour = INK,
           label = sprintf("Wilcoxon on 6 vs 8 patients\nP = %.2f", p_pat))

# ---- W4-3: composition ---------------------------------------------------------------------
mf2 <- c(F1 = 9, F2 = 12, F3 = 21, F4 = 23, F5 = 25, F6 = 28, F7 = 31, F8 = 36, C1 = 3, C2 = 5, C3 = 6, C4 = 8, C5 = 13, C6 = 15)
set.seed(21)
other_myo <- round(c(runif(8, 14, 24), runif(6, 6, 14)))
comp <- tibble(patient = names(mf2), condition = factor(ifelse(grepl("^F", names(mf2)), "Fibrosis", "Control"), levels = c("Control", "Fibrosis")),
               MF2 = mf2, `Other myofibroblasts` = other_myo) |>
  mutate(`Other fibroblasts` = 100 - MF2 - `Other myofibroblasts`)
p_mf2 <- wilcox.test(MF2 ~ condition, data = comp, exact = TRUE)$p.value
stopifnot(abs(median(comp$MF2[comp$condition == "Fibrosis"]) - 24) < 1e-9, abs(median(comp$MF2[comp$condition == "Control"]) - 7) < 1e-9)
long <- comp |> pivot_longer(c(MF2, `Other myofibroblasts`, `Other fibroblasts`), names_to = "state", values_to = "pct") |>
  mutate(state = factor(state, levels = c("Other fibroblasts", "Other myofibroblasts", "MF2")))
SCOL <- c(`Other fibroblasts` = "#DADADC", `Other myofibroblasts` = GREY2, MF2 = KEY)
pie_df <- long |> group_by(condition, state) |> summarise(pct = mean(pct), .groups = "drop")
p_pie <- ggplot(pie_df, aes(x = "", y = pct, fill = state)) + geom_col(width = 1, colour = "white", linewidth = 0.3) +
  coord_polar(theta = "y") + facet_wrap(~ condition) + scale_fill_manual(values = SCOL) +
  theme_void(base_family = FAM, base_size = 10) +
  theme(strip.text = element_text(face = "bold", colour = INK, margin = margin(b = 4)), legend.position = "bottom",
        legend.title = element_blank(), legend.key.size = unit(3, "mm"),
        plot.title = element_text(face = "bold", size = 10.5, colour = AVOID, margin = margin(b = 6)), plot.title.position = "plot",
        plot.margin = margin(6, 10, 6, 6))
ord <- comp |> arrange(condition, MF2) |> pull(patient)
p_stack <- ggplot(long |> mutate(patient = factor(patient, levels = ord)), aes(patient, pct, fill = state)) +
  geom_col(width = 0.75) + facet_grid(~ condition, scales = "free_x", space = "free_x") +
  scale_fill_manual(values = SCOL, breaks = c("MF2", "Other myofibroblasts", "Other fibroblasts")) +
  scale_y_continuous(expand = c(0, 0)) + labs(x = "Patient", y = "Share of fibroblasts (%)") +
  annotate("text", x = Inf, y = Inf, label = "", family = FAM) +
  theme(legend.position = "bottom", legend.title = element_blank(), legend.key.size = unit(3, "mm"),
        axis.text.x = element_text(size = 8))

save_pair <- function(left, right, week, name, lang, h = 70) {
  g <- (left | right) + plot_layout(widths = c(1, 1))
  ggsave(out(week, name, lang), g, width = 180, height = h, units = "mm", device = svg, bg = "white")
}
for (lang in c("ko", "en")) {
  t <- TXT[[lang]]
  save_pair(avoid_title(p_bar + ggtitle(t$a1)), p_dot + ggtitle(t$a2), "w04", "graph_few_samples", lang)
  save_pair(avoid_title(p_v_bad + ggtitle(t$b1)), p_v_good + ggtitle(t$b2), "w04", "graph_cells_as_n", lang)
  save_pair(p_pie + ggtitle(t$c1),
            p_stack + ggtitle(t$c2) + labs(caption = sprintf("MF2 median %d%% vs %d%%, Wilcoxon %s",
                                                              24, 7, sprintf("P = %.3f", p_mf2))) +
              theme(plot.caption = element_text(colour = GREY2, size = 8.5)),
            "w04", "graph_composition", lang, h = 82)
}

# ---- W5: mock Figure 2 ---------------------------------------------------------------------
tk <- TukeyHSD(aov(area ~ group, data = fib))$group
p_sv <- tk["UUO + vehicle-sham", "p adj"]; p_vx <- tk["UUO + compound X-UUO + vehicle", "p adj"]
panel_a <- ggplot() +
  geom_rect(data = tibble(i = 1:3), aes(xmin = (i - 1) * 1.1, xmax = (i - 1) * 1.1 + 1, ymin = 0, ymax = 1),
            fill = "#EAEBEB", colour = "#DADADC", linewidth = 0.3) +
  geom_text(data = tibble(i = 1:3, l = GROUPS), aes(x = (i - 1) * 1.1 + 0.5, y = 1.09, label = l),
            family = FAM, size = 3.3, colour = INK, fontface = "bold") +
  geom_text(data = tibble(i = 1:3), aes(x = (i - 1) * 1.1 + 0.5, y = 0.55, label = "representative\nimage"),
            family = FAM, size = 3, colour = GREY2) +
  geom_segment(data = tibble(i = 1:3), aes(x = (i - 1) * 1.1 + 0.62, xend = (i - 1) * 1.1 + 0.92, y = 0.08, yend = 0.08),
               linewidth = 0.9, colour = INK) +
  coord_fixed(xlim = c(-0.02, 3.22), ylim = c(-0.02, 1.16), expand = FALSE) + theme_void(base_family = FAM)
yb <- c(24.5, 28.5)
panel_b <- p_dot + scale_y_continuous(limits = c(0, 31), expand = c(0, 0)) +
  annotate("segment", x = c(1, 2), xend = c(2, 3), y = yb, yend = yb, linewidth = 0.3, colour = INK) +
  annotate("text", x = c(1.5, 2.5), y = yb + 1.4, label = c(fmtp(p_sv), fmtp(p_vx)), family = FAM, size = 3.2, colour = INK)
fig2 <- (panel_a | panel_b) + plot_layout(widths = c(1.55, 1)) +
  plot_annotation(tag_levels = "a") & theme(plot.tag = element_text(face = "bold", size = 12, family = FAM, colour = INK))
suppressWarnings(ggsave(out("w05", "figure2_mock", "ko"), fig2, width = 180, height = 72, units = "mm", device = svg, bg = "white"))

cat(sprintf("fibrotic area means: %s\n", paste(round(tapply(fib$area, fib$group, mean), 2), collapse = ", ")))
cat(sprintf("fibrotic area SDs: %s\n", paste(round(tapply(fib$area, fib$group, sd), 2), collapse = ", ")))
cat(sprintf("Tukey: sham vs vehicle %s, vehicle vs compound X %s (P = %.5f)\n", fmtp(p_sv), fmtp(p_vx), p_vx))
cat(sprintf("Acta2: cells n = %d, cell-level P = %.2e, patient-level P = %.3f\n", nrow(cells), p_cell, p_pat))
cat(sprintf("MF2 medians 24 vs 7, Wilcoxon exact P = %.5f\n", p_mf2))
