以下是这两页内容的中文翻译：

---

### 第 114 页

然后，如果需要高度细化的细节，可以使用某种类型的蒙特卡洛模拟（Monte Carlo simulation）。通常情况下，并不需要蒙特卡洛模拟所提供的高精细度。

---

### 术语定义

我们在此使用的许多术语都来自统计学。为避免混淆，我们在表 4-1 中对这些术语进行了定义。

#### 表 4-1 核心统计学术语

| 术语（Term） | 定义（Definition） |
| :--- | :--- |
| **随机变量**<br>(Random variable) | 一种数学实体，它将随机事件的结果“映射”到实数集中。例如，抛硬币可以映射为：正面为 1，反面为 0。 |
| **均值 / 期望值**<br>(Mean) | 随机变量的期望值。<br>$$\mu = E[X] = \int_{-\infty}^{\infty} s f(s) \, ds$$<br>字母 $\lambda$ 有时用于表示平均速率（例如需求率）。 |
| **样本均值**<br>(Sample mean) | 随机变量的算术平均值。<br>$$\bar{X} = \frac{\sum_{i=1}^{n} X_i}{n}$$ |
| **方差**<br>(Variance) | $$\sigma^2 = \text{VAR}(X) = \int_{-\infty}^{\infty} f(s)(s - \mu)^2 \, ds$$ |
| **标准差**<br>(Standard deviation) | $$\sigma = \sqrt{\text{VAR}(X)}$$ |
| **样本方差**<br>(Sample variance) | $$S^2 = \frac{\sum_{i=1}^{n} X_i^2 - n\bar{X}^2}{n - 1}$$ |
| **变异系数**<br>(Coefficient of variation) | $$\text{CV} = \frac{\sigma}{\mu}$$ |
| **变异系数平方**<br>(Squared coefficient of variation) | $$\text{SCV} = \frac{\sigma^2}{\mu^2}$$ |
| **平均日需求量**<br>(Mean daily demand) | $\lambda$ |
| **日需求量方差**<br>(Variance of daily demand) | $\sigma_d^2$ |

*(续)*

---

### 第 115 页

#### 表 4-1 核心统计学术语（续）

| 术语（Term） | 定义（Definition） |
| :--- | :--- |
| **平均补货时间**<br>(Mean replenishment time) | $\ell$ |
| **补货时间方差**<br>(Variance of replenishment times) | $\sigma_\ell^2$ |
| **再订货点**<br>(Reorder point) | $r$ |
| **订货批量**<br>(Reorder quantity) | $Q$ |
| **安全库存**<br>(Safety stock) | $s$ |
| **可用天数 / 库存周转天数**<br>(Days of supply) | $\text{DoS}$ |
| **存货点的平均现有库存**<br>(Mean on-hand inventory in a stock point) | $\bar{I}$ |
| **平均在订量（或在制品）**<br>(Mean on order (or WIP)) | $\bar{W}$ |
| **平均缺货积压水平**<br>(Mean backorder level) | $\bar{B}$ |
| **不发生缺货的概率（满足率）**<br>(Probability of not being stocked out (fill rate)) | $\bar{S}$ |
| **平均有效加工时间**<br>(Mean effective process time) | $t_e$ |
| **加工时间的变异系数平方**<br>(Squared coefficient of variation of process time) | $\text{SCV\_e}$ |

---

### 库存建模（MODELING STOCKS）

库存（Stocks）比流动（Flows）更容易建模，因此我们将从库存开始。它们更容易建模的原因在于：获取库存所需的转换过程（即采购时间），可以通过描述补货时间均值和标准差的参数来表征。而对于“流动”而言，这些时间必须通过更基础的参数计算得出，包括但不限于产能、需求、变异性、加工时间、设置（换产）时间以及机器数量等。对于“库存”，这些时间则是作为已知参数直接给出的。

#### 理想世界
在理想世界中，需求和转换过程都不存在任何变异。对于库存而言，这意味着管理者能够确切知道……