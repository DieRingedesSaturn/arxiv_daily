# ArXiv Daily Tracker

> 专注于高能天体物理与暂现源追踪，涵盖吸积物理、双星演化等。

## 监控配置
- **arXiv 分类**: `astro-ph.HE, astro-ph.SR`
- **ATel 范围**: 17680 之后
## 最新天文简报 (ATel)

### [3] | ATel 18043: [Further classifications at OHP of Gaia Alerted QSO candidates](https://www.astronomerstelegram.org/?read=18043)
- **日期**: 15 Sep 2026 UT | **源**: `Unknown`

**爆发速递**: 本ATel简报报道了利用上普罗旺斯天文台(OHP)1.93米望远镜对多颗Gaia警报的类星体及活动星系核候选体进行的后续光谱分类观测，给出了其红移及主要发射线特征。
**观测短评**: 虽然本研究属于活动星系核(AGN)范畴，但文章主要关注证认和低分辨率光谱分类，且目标多较暗或已过最佳跟进期，结合我方1m望远镜的能力与核心时变能谱研究兴趣，暂无须申请或进行光学后随观测。

---

### [6] | ATel 18042: [Radio Non-detection of Hercules X-1 during the ALS with MeerKAT/X-KAT](https://www.astronomerstelegram.org/?read=18042)
- **日期**: 14 Sep 2026 UT | **源**: `Hercules X-1`

**爆发速递**: MeerKAT望远镜利用X-KAT计划对处于异常低态(ALS)的中子星X-射线双星Hercules X-1进行了射电波段观测，在L波段未探测到射电辐射，给出3σ上限为81μJy/beam。
**观测短评**: 该目标为中子星X射线双星，符合课题组核心研究领域。由于属于射电未探测且处于X射线异常低态，暂无直接的光学后随需求或我方1米望远镜跟进价值，但对其多波段吸积状态的研究具有参考意义。

---

[查看本周完整 ATel](./atels/2026-W38.md)

[查看所有 ATel 索引](./atels/index.md)

---

## 最新论文 (arXiv)

*Tags: #arXiv #Astrophysics*

## 重点关注 (7篇)

### [10] | [Long-term X-ray spectral analysis of Cygnus X-1 using AstroSat](https://arxiv.org/abs/2609.12072v1)
**Authors**: H Lalthantluanga, Akash Garg, Ranjeev Misra et al. | **Targets**: Cygnus X-1

> *利用AstroSat对黑洞X射线双星Cygnus X-1长期光谱分析，提出双康普顿化模型解释软态和硬态特征。*

**研究背景**: 黑洞X射线双星天鹅座X-1（Cygnus X-1）在不同光谱态下的宽带X射线辐射机制长期备受关注，特别是软态下传统模型常遇到拟合不佳及物理参数反常的问题。

**数据方法**: 本研究利用AstroSat卫星在2016年至2019年间对天鹅座X-1进行的长期观测数据，对其硬态、中间态和软态开展了系统的X射线光谱分析与模型拟合。

**核心结论**: 研究发现常规单康普顿化加多色盘模型在软态下失效且内半径无物理意义。引入相对论盘模型虽能改善拟合但需极高的颜色修正因子。最终采用由热日冕和温日冕组成的双康普顿化模型成功实现了对全光谱态的优质拟合，揭示了双康普顿化过程对塑造该黑洞宽带X射线辐射的关键作用。

---

### [9] | [Nonuniform Particle Injection into Black Hole Jets by Radiative Magnetic Reconnection](https://arxiv.org/abs/2605.01002v3)
**Authors**: Rin Oikawa, Kenji Toma, Shigeo S. Kimura et al. | **Targets**: M87

> *研究了辐射磁重联中的非均匀粒子注入对活动星系核黑洞喷流的影响，并通过广义相对论光线追踪成功解释了M87喷流的射电辐射。*

**研究背景**: 理解黑洞喷流的等离子体来源及其辐射机制是天体物理学的重要前沿挑战。特别是如何解释观测到的喷流辐射，目前其物源机制仍不明确。

**数据方法**: 本研究基于三维广义相对论磁流体力学模拟，采用广义相对论射线追踪方法，在弯曲时空中考虑光子传播与碰撞角，计算了非轴对称磁 reconnection 产生的高能光子对产生率的空间分布。

**核心结论**: 研究发现，该机制在考虑光子各向异性时仍能自然提供充足的等离子体，以解释M87喷流的射电辐射。此外，旋转黑洞对正负电子对空间分布的塑造起关键作用，进而影响喷流加速及基底的高能辐射。

---

### [8] | [A Localized Current-Sheet Magnetic-Diffusion and Heating Prescription for Ideal-GRMHD Simulations of M87*-like Accretion Flows](https://arxiv.org/abs/2609.12377v1)
**Authors**: Songyan Dai (Zhejiang University), Renyue Cen (Zhejiang University) et al. | **Targets**: M87*

> *该论文提出了用于M87*类吸积流理想广义相对论磁流体动力学模拟的局域电流片磁扩散与加热算法。*

**研究背景**: 理想广义相对论磁流体动力学（Ideal-GRMHD）是黑洞吸积模型的核心，但无法自洽处理磁重联等耗散物理过程。本研究旨在开发一种局域电流片磁扩散与加热算法，以改善M87*等黑洞吸积流模拟。

**数据方法**: 研究基于Athena++代码实现，通过无量纲电流代理$\alpha_J$的光滑阈值选择磁扩散系数，并耦合保守能量通量修正。方法通过静态傅里叶、行波阿尔文及史瓦西开边界测试进行验证。

**核心结论**: 测试显示总能量残差低于 $2\times10^{-15}$。在M87*轴对称模拟中，局域扩散对早期及晚期平均磁通量和吸积率的影响均小于 $1.6\%$，远小于内在变率，且避免了全局均匀扩散造成的吸积率崩塌，实现了精确的局域耗散建模。

---

### [8] | [Orbital evolution of asymmetric binaries within accreting environments](https://arxiv.org/abs/2606.18341v2)
**Authors**: Albert Radulea, Marcelo E. Rubio, Konstantinos Kritos et al.

> *研究了超大质量黑洞吸积盘中致密天体的轨道演化，揭示了相对论效应与盘环境的相互作用，并探讨了与准周期爆发的潜在联系。*

**研究背景**: 嵌入吸积盘的极端质量比inspiral为研究相对论轨道动力学与环境效应的相互作用提供了理想场景，探讨此类系统在活动星系核盘中的长期演化对于理解其动力学及准周期爆发具有重要意义。

**数据方法**: 本工作纯基于理论框架，将紧致天体反复穿过超大质量黑洞吸积盘的长期演化建模，轨道运动采用克尔测地线描述，盘相互作用通过质量吸积和动力学摩擦的有效公式编码，并对比了牛顿近似及不同吸积盘模型。

**核心结论**: 盘致耗散驱动轨道面快速对齐盘面及后续较慢的偏心率阻尼。相对论效应在很大轨道分离处即产生偏差；相对论吸积盘结构预测更弱的耗散和更慢演化，而中心黑洞自旋影响较小，强调了精细建模的必要性。

---

### [7] | [Late-Time Evolution of the Massive Stellar Merger M101 OT2015-1](https://arxiv.org/abs/2609.12981v1)
**Authors**: Marco A. G\'omez-Mu\~noz, Nadejda Blagorodnova, Tomasz Kami\'nski et al. | **Targets**: M101 OT2015-1

> *利用多波段红外观测与辐射转移模型，研究了亮红新星M101 OT2015-1晚期的尘埃与分子演化过程。*

**研究背景**: 亮红新星（LRNe）源于密近双星的不稳定质量转移与共同包层演化，最终导致恒星合并。其膨胀的冷却喷出物为分子和尘埃形成提供了理想环境，本研究旨在探讨大质量LRN前身星 M101 OT2015-1 爆发约5年内的晚期尘埃与分子演化。

**数据方法**: 研究团队利用 NEOWISE、Spitzer、Keck 望远镜的 NIRC2 和 MOSFIRE 的多波段近红外与中红外观测数据，通过二维高斯过程回归进行插值。并结合一维球形辐射转移模型对光谱能量分布（SED）进行拟合，同时采用局部热力学平衡等温平板模型分析 CO 分子特征。

**核心结论**: 观测表明，爆发后 +200 天左右开始迅速凝结尘埃，并在约 +600 天出现近红外再次变亮与尘埃再加热现象，证实由激波相互作用驱动了第二阶段尘埃成核。光谱揭示其富氧环境、低光球膨胀速度及高 CO 柱密度，证实大质量前身星产生的 LRNe 是宇宙尘埃和分子的多产工厂。

---

### [6] | [Superoutbursts and Superhumps of Cataclysmic Variables observed with TESS](https://arxiv.org/abs/2609.12461v1)
**Authors**: Qi-Bin Sun, Sheng-Bang Qian, Li-Ying Zhu et al. | **Targets**: RZ LMi, ASASSN-14kj

> *利用TESS空间望远镜对30个SU UMa型激变变星的超爆发与超驼峰现象进行系统性光变分析。*

**研究背景**: SU UMa型激变变星的超大爆发与超驼峰是研究吸盘动力学的关键特征，但受限于地面观测，超驼峰演化行为的多样性长期缺乏全面约束。

**数据方法**: 本研究利用TESS卫星的高频光变曲线，对30颗SU UMa型矮新星的37次超大爆发事件展开了系统性分析。

**核心结论**: 研究探测到29个系统的超驼峰信号（5例首次发现），厘清了经典三阶段演化，测得18个系统的动力学质量比。结果揭示了超驼峰形态的内在可重复性，发现RZ LMi和ASASSN-14kj背离标准模板，并通过正常爆发期间持续的超驼峰证认了偏心吸盘结构的存续，深化了对吸盘动力学与潮汐进动模型的理解。

---

### [6] | [Heavy Seed Black Hole Growth in Metal-Enriched Halos through Disk-Induced Stellar Disruptions: A Semi-Analytical Modelling](https://arxiv.org/abs/2609.12619v1)
**Authors**: Zijian Wang, Zhili Wang, Yiqiu Ma et al.

> *本文利用半解析模型研究了重种子黑洞在金属增丰晕中通过盘诱导潮汐撕裂事件（TDE）的增长机制。*

**研究背景**: 近期模拟表明，重种子黑洞倾向于在弱金属富集的原子冷却晕中形成，并天然嵌入在Pop I/II核星团内。本研究旨在探讨这些恒星产生的潮汐瓦解事件（TDEs）能否为重种子黑洞提供高效且持续的成长途径。

**数据方法**: 研究构建了一个半解析模型，用于模拟重种子黑洞周围恒星轨道的衰减、吸积盘捕获、迁移及潮汐瓦解，并将该TDE贡献纳入包含重子与金属丰度演化的宇宙学合并树中。

**核心结论**: 结果显示，盘诱导的TDEs可主导重种子黑洞的早期生长，使其在形成后0.1亿年内质量增至$10^5 M_\odot$，并在前2亿年内贡献了可与气体吸积媲美的质量，有效缓解了高红移极端黑洞候选体与模型的张力。

---

## 其他相关 (32篇)

- **[3]** [Constraining dark matter using 20-year INTEGRAL/IBIS observations I: Primordial black holes](https://arxiv.org/abs/2609.12044v1)
  - *利用20年INTEGRAL/IBIS硬X射线观测数据限制原初黑洞暗物质成分。*
- **[3]** [Time-Integrated Searches for Sub-TeV Neutrino Sources with IceCube-DeepCore](https://arxiv.org/abs/2609.12055v1)
  - *利用IceCube-DeepCore的11.1年数据进行了亚太电子中微子源的时间积分搜索，未发现显著信号。*
- **[3]** [Electromagnetic Probes of the Supernova Engine](https://arxiv.org/abs/2609.12308v1)
  - *本文综述了利用电磁波探测超新星爆发引擎及极端物理的观测诊断与理论模型。*
- **[3]** [Constraining Ultralight Scalars with Black Hole Binary Mergers in Galactic Nuclei](https://arxiv.org/abs/2609.12052v1)
  - *利用LIGO-Virgo-KAGRA引力波目录中的黑洞双星合并率来约束超轻标量粒子。*
- **[3]** [Accretion onto a moving black hole for stiff equations of state](https://arxiv.org/abs/2609.12058v1)
  - *本文通过数值模拟研究了刚性状态方程下流体向运动史瓦西黑洞的吸积过程，重点关注大绝热指数下的吸积率和拖曳率。*
- **[3]** [A Proliferated Space Architecture for Time-Domain Astrophysics](https://arxiv.org/abs/2609.12153v1)
  - *本文介绍了Hydra星座概念，一种用于时域和多信使天体物理学的大规模分布式空间观测架构。*
- **[2]** [Identifying Kilonovae in the Presence of Optical Afterglow for the Wide Field Survey Telescope](https://arxiv.org/abs/2607.20233v2)
  - *该论文评估了广域巡天望远镜（WFST）在光学余辉干扰下识别双中子星并合产生的千新星的性能与观测策略。*
- **[1]** [The influence of free-free absorption on the radio spectrum of Particle-Accelerating Colliding-Wind Binaries](https://arxiv.org/abs/2609.12907v1)
  - *该论文研究了大质量恒星碰撞风双星中自由-自由吸收对非热射电辐射及粒子加速观测偏差的影响。*
- **[1]** [An efficient approach to resistive GRMHD simulations of binary neutron star mergers](https://arxiv.org/abs/2609.12998v1)
  - *提出了一种高效的电阻广义相对磁流体动力学数值模拟方法，并应用于双中子星合并研究。*
- **[1]** [Implications of the LISA stochastic signal from eccentric stellar mass black hole binaries in vacuum](https://arxiv.org/abs/2605.05537v2)
  - *该文研究了LISA探测器可观测的恒星级黑洞双星随机引力波背景及偏心率的影响。*
- **[1]** [Mass-Orbital Period Distribution of Massive White Dwarfs Formed Through Stable Mass Transfer](https://arxiv.org/abs/2606.06141v3)
  - *利用MESA研究稳定质量转移形成的重白矮星及其质量-轨道周期分布。*
- **[1]** [The Heavy Tailed Non-Gaussianity of the Supermassive Black Hole Gravitational Wave Background](https://arxiv.org/abs/2604.08506v2)
  - *该论文研究了超大质量黑洞双星产生的引力波背景的非高斯性及脉冲星计时残差分布特征。*
- **[1]** [Time-Domain Dust Astrophysics. I. Polarization Flares, Polarization-Angle Reverberation, and Fossil Imprints in Supernova-Illuminated Clouds](https://arxiv.org/abs/2607.24517v2)
  - *本文利用TransRAT框架预测了超星系团照明下致密云中尘埃偏振随时间的演化特征。*
- **[1]** [Oscillations of Dissipative Neutron Stars: The Impact of Hyperonic Reaction Rates](https://arxiv.org/abs/2608.07311v2)
  - *该论文研究了含超子中子星的耗散振荡及有限反应速率对潮汐动力学的影响。*
- **[0]** [Plasma Heating and Energization in Hot-Onset Flare Precursor Events](https://arxiv.org/abs/2609.12215v1)
  - *本文利用动理学宏观模型研究了太阳耀斑热初始阶段的等离子体加热与磁重联机制。*
- **[0]** [Evolution of first-interaction second-harmonic anisotropy in cosmic-ray air showers](https://arxiv.org/abs/2609.12380v1)
  - *本文利用CORSIKA模拟研究了广阔大气簇射中由首次相互作用继承的二次谐波各向异性的纵向演化。*
- **[0]** [Magnetic Fields and Asymmetric Accretion in the Class 0 Protostellar System L1527 IRS](https://arxiv.org/abs/2609.12467v1)
  - *本文利用多波段观测研究了Class 0原恒星系统L1527 IRS的磁场形态与不对称吸积特征。*
- **[0]** [Spin-polarization of the neutron ocean in magnetar crusts](https://arxiv.org/abs/2609.12539v1)
  - *该论文研究了磁星强磁场下中子星壳层中自由中子的自旋极化效应对其结构的影响。*
- **[0]** [Large-Scale Latitude-time Relationships Between the Green-Line Corona and Sunspot Activity During Solar Cycles 18-24](https://arxiv.org/abs/2609.12644v1)
  - *本文研究了第18-24太阳活动周期间绿线日冕与太阳黑子活动之间的大尺度纬度-时间关系及其时滞关联。*
- **[0]** [Plasmoid-Trapped Condensation Associated with a Transient Thermal-Instability-Like Process in Chromospheric Magnetic Reconnection](https://arxiv.org/abs/2609.12699v1)
  - *本文利用磁流体动力学模拟研究了色球层磁重联中等离子体团内的热不稳定性凝聚过程。*
- **[0]** [Reconsidering the role of bright and dark gravitational-wave standard sirens for cosmology](https://arxiv.org/abs/2609.12053v1)
  - *该论文研究引力波标准警报器（明亮与黑暗警报器）在宇宙学中的应用与局限性。*
- **[0]** [Intrinsic pressure anisotropy in spherical Proca stars](https://arxiv.org/abs/2609.12773v1)
  - *本文从爱因斯坦-复Proca理论出发，推导并分析了球形Proca星中的内禀压力各向异性。*
- **[0]** [Reconstructing the Dark Matter Equation of State with Compact Object Inspirals](https://arxiv.org/abs/2609.12806v1)
  - *本文研究了致密双星在暗物质包层中旋进产生的引力波环境效应，并探讨了利用引力波观测重建暗物质状态方程的方法。*
- **[0]** [XMST: An Extended Minimum Spanning Tree Framework with Objective Fracture-Scale Selection](https://arxiv.org/abs/2609.12943v1)
  - *本文提出了一种基于扩展最小生成树和客观断裂尺度选择框架的恒星空间结构识别方法。*
- **[0]** [Magnetized interstellar molecular clouds - III. Filament Collisions and Core Formation: Insights into Substructures and Evolution](https://arxiv.org/abs/2609.12989v1)
  - *本文利用磁流体动力学模拟研究了分子云中纤维状结构的形成及致密云核的演化过程。*
- **[0]** [Induced Scattering of Strong Waves in Pair Plasmas](https://arxiv.org/abs/2604.15798v2)
  - *该论文研究了对子等离子体中强电磁波的受激散射及其对快速射电暴传播的影响。*
- **[0]** [Solar Wind Proton Heating and its Effect on Temperature Anisotropy Evolution between 0.05 and 1 au](https://arxiv.org/abs/2607.25824v2)
  - *该论文研究了太阳风质子在内日球层的加热及温度各向异性演化。*
- **[0]** [Active nests at solar maximum: How nested flux emergence dominated flaring activity and structured the heliosphere](https://arxiv.org/abs/2608.26315v2)
  - *本文利用多视角观测研究了太阳活动峰值期间活动巢的形成及其对太阳耀斑活动和大尺度磁场的影响。*
- **[0]** [Origin of small-scale evaporation flows deep in the chromosphere during a solar flare](https://arxiv.org/abs/2608.29649v2)
  - *本文利用高分辨率观测研究了太阳耀斑色球层深处的小尺度蒸发流及其起源。*
- **[0]** [On the Theory of Bulk Viscosity of Cold Plasmas and Thermodynamics of Alkali-Noble Gas Cocktails](https://arxiv.org/abs/2511.14790v5)
  - *本文研究了冷等离子体的总体积黏滞性与碱-稀有气体混合物的热力学理论，与本课题组的黑洞、暂现源或吸积物理研究领域无关。*
- **[0]** [Hedorah, the first yellow supergiant Kaiju star candidate at $z=3.7$ revealed by JWST behind AS1063](https://arxiv.org/abs/2601.11704v2)
  - *利用JWST数据对星团AS1063建立透镜模型，并发现了高红移的黄超巨星候选体Hedorah。*
- **[0]** [Gas distributions inside and around haloes in the alternative dark matter simulations AIDA-TNG](https://arxiv.org/abs/2601.18578v2)
  - *该论文利用AIDA-TNG宇宙学模拟研究了不同暗物质模型对晕内及周围气体和中性氢分布的影响。*

[查看历史目录](./posts/index.md)
