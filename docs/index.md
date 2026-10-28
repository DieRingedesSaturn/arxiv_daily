# ArXiv Daily Tracker

> 专注于高能天体物理与暂现源追踪，涵盖吸积物理、双星演化等。

> [RSS 订阅](https://DieRingedesSaturn.github.io/arxiv_daily/feed_rss_created.xml) — 每日更新自动推送

## 监控配置
- **arXiv 分类**: `astro-ph.HE, astro-ph.SR`
- **ATel 范围**: 17680 之后
## 最新天文简报 (ATel)

### [3] | ATel 18120: [Nova Tau 2026 (V1452 Tau) is likely undergoing dust formation](https://www.astronomerstelegram.org/?read=18120)
- **日期**: 27 Oct 2026 UT | **源**: `V1452 Tau`

**爆发速递**: NMW-TexasTech巡天发现暂现源TCP J05210763+2338194，后被证认为新星Nova Tau 2026（V1452 Tau）。近期多地望远镜监测显示其在经历约70天平台期后亮度急剧下降，光谱证实这是由于喷出物中发生尘埃凝结。
**观测短评**: 该目标属于新星（CV相关），虽然具备光学后随监测价值，但其目前亮度及演化阶段已有大量专业中小望远镜跟进，且不符合本组核心的黑洞及AGN研究方向，暂无必要申请我方1m望远镜或大型设备机时。

---


[查看本周完整 ATel](./atels/2026-W44.md)

[查看所有 ATel 索引](./atels/index.md)

---

## 最新论文 (arXiv)

*Tags: #arXiv #Astrophysics*

## 重点关注 (12篇)

### [10] | [Accretion Flow Properties of MAXI J1834-021 during Its Multi-peaked Outburst in 2023](https://arxiv.org/abs/2504.16398v3)
**Authors**: Dipak Debnath, Hsiang-Kuang Chang et al. | **Targets**: MAXI J1834-021

> *利用NICER数据研究了银河系黑洞候选体MAXI J1834-021在2023年多次爆发中的时变与能谱特性。*

**研究背景**: 银河系暂现黑洞候选体 MAXI J1834-021 在2023年经历了长达约10个月的“微弱”爆发活动。研究其时变与光谱演化，旨在揭示该多峰爆发事件中的吸积流动力学性质。

**数据方法**: 本工作利用 NICER 望远镜在2023年3月至10月期间的观测数据，系统分析了硬/软能段光子计数率、硬度比及准周期振荡（QPO）频率，并分别采用了唯象模型（diskbb+powerlaw）和物理模型（两成分平流吸积流，TCAF）进行了光谱拟合。

**核心结论**: 观测表明该源在全过程中持续处于硬光谱态，无软态出现，属于一次“失败”的爆发。低频 QPO 在主爆发阶段呈现频率单调降低的演化。TCAF 模型拟合估计其黑洞质量为 $12.4\pm1.7~M_\odot$，证实了热康普顿云非热辐射的主导地位。

---

### [10] | [On the Physical Origins of the Millimeter Fundamental Plane in Active Galactic Nuclei](https://arxiv.org/abs/2601.10612v2)
**Authors**: Kratika Mazde, Angelo Ricarte, George N. Wong et al.

> *利用广义相对论磁流体动力学模拟研究活动星系核毫米波基本平面的物理起源与吸积物理。*

**研究背景**: 活动星系核观测揭示了毫米波光度、X射线光度与黑洞质量之间存在基本平面关系统计规律，暗示这三个波段的辐射源自共同的物理机制，该研究旨在探究这一相关性的潜在物理起源。

**数据方法**: 研究基于一组包含动力学重要磁场的广义相对论磁流体动力学（GRMHD）模拟，通过射线追踪计算生成了涵盖同步辐射、韧致辐射及康普顿散射的全光谱模型。

**核心结论**: 模拟自然重现了观测关系且无需调参。研究发现逆康普顿散射在X射线产生中占主导地位，且黑洞自旋影响较小，证实致密热吸积流可自然解释低光度活动星系核的多波段特性。

---

### [9] | [FEADME: Fast Elliptical Accretion Disk Modeling Engine](https://arxiv.org/abs/2512.10228v3)
**Authors**: Nicholas Earl, K. Decker French, Jason T. Hinkle et al.

> *该论文开发了基于GPU加速的椭圆吸积盘模型框架，并将其成功应用于活动星系核与潮汐撕裂事件的光谱拟合。*

**研究背景**: 宽巴耳末线发射是研究致密天体周围吸积盘结构的关键探针。如何高效且自洽地分析大样本双峰发射线星系及潮汐瓦解事件（TDE）中的吸积盘几何与运动学特征，一直是观测研究的难点。

**数据方法**: 本文开发了基于 GPU 加速的 Python 框架 FEADME，利用 JAX 和 NumPyro 实现可微分正演建模与贝叶斯推断。研究对 237 个双峰发射线活动星系核（AGN）和 5 个 TDE 的 $\alpha$ 发射线进行了系统拟合。

**核心结论**: 结果显示，AGN 呈现多样化的吸积盘几何形态，而 TDE 倾向于更低的偏心率。研究发现椭圆盘模型给出的物理参数极大地依赖于对轮廓不对称性的处理，且多数源支持吸积盘与各向同性风共存的物理图像，彰显了 FEADME 在大样本星系演化研究中的重要价值。

---

### [9] | [The study of the circumnuclear environment of accreting supermassive black holes with realistic X-ray spectral models](https://arxiv.org/abs/2605.06794v2)
**Authors**: Georgios Dimopoulos, Claudio Ricci, St\'ephane Paltani et al. | **Targets**: NGC 424

> *本文利用真实的几何构型开发了新型X射线光谱模型，用于研究活动星系核（AGN）超大质量黑洞周围的环核物质环境。*

**研究背景**: X射线光谱建模是研究活动星系核（AGN）超大质量黑洞周围环境的关键工具。然而，过去常用的模型多采用平板或圆环等简化几何构型，缺乏真实性，限制了对复杂核周物质物理性质的深入理解。

**数据方法**: 研究团队利用光线追踪代码 RefleX 生成了宽能段的全新X环境光谱模型，并推出了两个公开的表格模型：包含尘埃环与极性空心锥的 RXToPo 模型，以及进一步增设吸积盘与宽线区的 RXagn1 模型，并将其应用于 NGC 424 的X射线光谱分析中。

**核心结论**: 该研究通过采用更符合实际天体物理环境的几何构型，成功模拟了X射线发射以再处理辐射为主的源。这验证了新模型在解析复杂 AGN 核周物质结构方面的巨大潜力，推动了对超大质量黑洞吸积环境的认知。

---

### [8] | [Constraint on magnetized black bounce spacetime from HFQPOs data and the selection of resonance models via information criterion](https://arxiv.org/abs/2512.12557v2)
**Authors**: Shining Yang, Jianbo Lu, Mou Xu et al. | **Targets**: GRS 1915+105, XTE 1550-564, GRO 1655-40

> *利用微类星体的高频QPO数据对磁化黑弹跳时空及共振模型进行限制与评估。*

**研究背景**: 辛普森-维瑟（Simpson-Visser, SV）黑弹时空统一描述了史瓦西黑洞、常规黑洞与虫洞。本研究旨在探讨磁化SV时空中带电粒子的动力学，并利用高频准周期振荡（HFQPOs）数据对其正则化参数及周围磁场进行严格约束。

**数据方法**: 研究结合了微类星体 GRS 1915+105、XTE 1550-564 和 GRO 1655-40 的 HFQPO 观测数据进行 $\chi^2$ 分析。同时，采用赤池信息准则（AIC）、贝叶斯信息准则（BIC）及贝叶斯因子对多种 epicyclic 共振模型及其变体进行了评估与筛选。

**核心结论**: 磁场显著影响最内稳定圆轨道及频闪运动频率。AIC表明 $ER_8$ 模型最优，$ER_3$ 次之。在受支持的模型中，正则化参数约束为 $0\leq a/M<0.736$，表明HFQPO数据支持该时空作为常规黑洞，并暗示了量子效应的存在。

---

### [7] | [Accreting Neutron Stars in Low-Mass X-ray Binaries](https://arxiv.org/abs/2610.10691v2)
**Authors**: M. C. Baglio, S. E. Motta, A. P. Nitindala et al.

> *该综述总结了中子星低质量X射线双星的吸积盘、时变、热核爆发、喷流及X射线偏振观测研究。*

**研究背景**: 中子星低质量X射线双星由于拥有实体表面与磁场，是研究高能天体物理与致密物质物理的独特实验室。本文旨在系统梳理该领域从外盘到恒星表面的物质吸积物理机制。

**数据方法**: 本文基于数十年的多波段观测发现，综合评述了环礁源、Z源、超紧凑X射线双星、吸积毫秒脉冲星及过渡型毫秒脉冲星等主要系统，并纳入了成像X射线偏振探测器（IXPE）的最新X射线偏振结果与光红外偏振观测。

**核心结论**: 研究揭示了光谱态、时变及多波段行为中编码的内吸积流物理，阐明了I型X射线暴、边界层、相对论性喷流与电离盘风的作用。IXPE的偏振数据首次为传统光谱无法解析的吸积盘、电晕、扩展层和喷流发射区几何提供了新约束。

---

### [6] | [The evolutionary history of ultra-compact accreting binaries. II. HST spectroscopy of two eclipsing AM CVn stars](https://arxiv.org/abs/2610.36066v1)
**Authors**: W. Yu, A. F. Pala, T. Kupfer et al. | **Targets**: YZ LMi, ZTF J0407-00

> *利用哈勃望远镜对两个食AM CVn星系进行紫外光谱分析，测量其白矮星大气丰度并约束其演化通道。*

**研究背景**: AM CVn星是一类超致密致吸积双星，作为mHz引力波源和Ia型超新星候选前身星备受关注。然而其存在白矮星、氦星和激变变星三种演化通道，长期存在争议。

**数据方法**: 本文利用哈勃太空望远镜（HST）获取的紫外光谱，对两颗食双星YZ LMi和ZTF J0407-00的吸积白矮星大气进行了详细建模，通过测量氮碳丰度比来追踪供体星的核燃烧历史。

**核心结论**: 研究测定了两颗白矮星的有效温度、表面重力及质量。由于两系统均未检测到碳，推导出了极高的氮碳质量比（N/C > 117和 > 185），这排除了氦星演化通道，更支持白矮星通道。

---

### [6] | [2:1 Harmonics in the Radio Light Curves of Supermassive Black Hole Binary Candidates](https://arxiv.org/abs/2610.36732v1)
**Authors**: A. C. S. Readhead, M. F. Aller, R. D. Blandford et al. | **Targets**: PKS J0805-0111, PKS 2131-021, J1309+1154

> *本文分析了超大质量黑洞双星候选体射电光变曲线中的2:1谐波周期性，探讨了其物理模型及在耀变体搜寻中的意义。*

**研究背景**: 寻找超大质量黑洞双星（SMBHB）对于理解星系演化至关重要。然而，耀变体光变曲线常伴随相关随机噪声，且观测周期普遍超两年且可能长时间消失，如何确证周期真实性是当前领域的关键难点。

**数据方法**: 本研究利用欧文斯谷射电天文台（OVRO）与密歇根大学射电天文台（UMRAO）的长期监测数据，对耀变体候选体进行了细致的周期分解与光变分析，并提出了四种可解释2:1谐波公度性的物理模型。

**核心结论**: 研究在PKS J0805-0111和PKS 2131-021中发现了2:1谐波周期性证据（继J1309+1154之后）。这表明2:1谐波可能是确认SMBHB候选体及揭示其中心引擎差异的关键特征，对推动耀变体周期性研究具有重要意义。

---

### [6] | [Self lensing in BH-NS binaries as progenitors for periodically repeating Fast Radio Bursts](https://arxiv.org/abs/2610.37052v1)
**Authors**: L. E. Rodr\'iguez, M. Cruces, G. Voisin et al. | **Targets**: SGR 1935+2154

> *探讨了黑洞-中子星双星中的自引力透镜效应对产生周期性重复快速射电暴的影响。*

**研究背景**: 快速射电暴（FRB）起源成谜，部分具有周期性活动窗口。中子星虽是热门候选者且银河系磁星SGR 1935+2154曾发出类FRB爆发，但其脉冲能量仍远低于观测到的FRB，本研究旨在探讨黑洞-中子星（BH-NS）双星系统的自引力透镜效应对弥补这一能量差距的潜力。

**数据方法**: 研究构建了包含轨道及朗斯-蒂林（Lense-Thirring）进动的简单BH-NS双星理论模型，采用圆轨道计算了脉冲沿轨道的引力透镜放大效应，并分析了脉冲分裂、时间延迟、能量分布及活动窗口。

**核心结论**: 引入进动的后开普勒轨道可产生数天至数十天的活动窗口；透镜效应将中子星对数正态能量分布转化为幂律尾巴；由毫秒级延迟推断的黑洞质量在中等质量黑洞（$10^3-10^4 M_\odot$）范围内。然而，该透镜放大仍不足以填补中子星与FRB间的能量鸿沟，加之系统丰度低，该通道可能较为罕见。

---

### [6] | [An SRG/eROSITA Study of Be X-ray binaries in Quiescence](https://arxiv.org/abs/2610.37277v1)
**Authors**: Ajith Balu, Kinjal Roy, Biswajit Paul et al.

> *利用eROSITA巡天数据对宁静态Be/X射线双星进行X射线能谱分析，探讨低吸积率下的辐射与吸积机制。*

**研究背景**: 贝塔射线双星（BeXRBs）通常包含中子星与Be星，绝大多数时间处于宁静态。研究其宁静态有助于深入探讨低质量吸积率下的X射线辐射机制。

**数据方法**: 本研究利用“光谱-伦琴-伽马”（SRG）卫星搭载的eROSITA望远镜首次全天巡天（eRASS1）数据，对BeXRBs的宁静态进行了综合分析，采用幂律模型和黑体模型对其光谱进行拟合，并计算了未探测到源的光度上限。

**核心结论**: 探测到的宁静态BeXRBs在多数情况下的X射线光度约为 $10^{33-36}$ erg s$^{-1}$，黑体模型表明辐射源自中子星表面的一部分。该结果可用于区分抛桨区吸积或冷吸积盘等低质量吸积模型，并与以往多台X射线天文台的数据进行了对比。

---

### [6] | [$\gamma$-ray variability of changing-look blazars: FSRQ-like jet behaviour](https://arxiv.org/abs/2610.37303v1)
**Authors**: Zahoor Malik, B. van Soelen, Sikandar Akbar et al.

> *利用Fermi-LAT长达17.9年的光变数据研究变脸耀变体的伽马射线变率，探讨其喷流与吸积物理机制。*

**研究背景**: 变脸耀变体（CLBs）在平谱射电类星体与BL Lac天体之间转变。其物理机制存在争议：是吸积盘状态发生改变，还是增强的喷流连续谱淹没了宽发射线？长期平均数据无法区分，需要通过伽马射线观测探究喷流性质以厘清本质。

**数据方法**: 本研究利用了长达17.9年的费米大天区空间望远镜（Fermi-LAT）在3、7和30天时间分辨率下的伽马射线光变曲线，并将CLBs与精心筛选和分析的BL Lac及FSRQ对照样本进行了对比。

**核心结论**: CLBs的相对光变幅度和爱丁顿比标度盘光度均与FSRQ无法区分，且显著高于BL Lac。CLBs的伽马射线喷流行为倾向于支持“可变喷流连续谱”假说，而非吸积盘机制的转变。

---

### [6] | [Eclipse Properties and Superhump Evolution in the SU UMa-Type Dwarf Nova Z Cha](https://arxiv.org/abs/2609.10966v2)
**Authors**: Qi-Bin Sun, Sheng-Bang Qian, Li-Ying Zhu et al. | **Targets**: Z Cha

> *利用TESS高频测光数据研究激变变星Z Cha的掩食特性与超驼峰演化。*

**研究背景**: 大视场时域巡天为理解激变变星的吸积盘演化带来了机遇与挑战。本研究旨在利用日食这一天然探针，深入剖析SU UMa型矮新星Z Cha的吸积盘结构与超驼峰演化规律。

**数据方法**: 本研究基于TESS卫星的高时间分辨率测光数据，系统分析了Z Cha在超爆发及宁静态下的日食深度变化、掩食极小的O-C（观测减计算）残差以及正超驼峰（PSH）振幅的演化特征。

**核心结论**: 研究发现超爆发期间三者具共同的~2天准周期调制，证实了偏心进动盘的存在。在宁静态下观测到PSH振幅与周期的线性减小，并首次在同期间探测到可能源自内盘逆向进动的负超驼峰（NSH）候选信号，若得证实将对经典倾斜盘模型提出新挑战。

---

## 其他相关 (41篇)

- **[4]** [X-ray Emission Study of TeV Blazars](https://arxiv.org/abs/2610.37114v1)
  - *本文利用Swift和NuSTAR对85个TeV耀变体进行了X射线能谱与时变分析。*
- **[3]** [An intermediate-mass stripped star with a dark companion in the Small Magellanic Cloud](https://arxiv.org/abs/2610.36050v1)
  - *在小麦哲伦星系发现了一个带有暗伴星的中等质量剥离星，伴星极可能是中子星。*
- **[3]** [Dynamical constraints on the companion mass from pulsar timing and cyclotron line confirmation in the SFXT IGR J16418-4532](https://arxiv.org/abs/2610.36103v1)
  - *利用NuSTAR和RXTE数据分析超巨星快X射线暂现源IGR J16418-4532的时变与能谱，测定其脉冲星自转周期、轨道参数及回旋吸收线。*
- **[3]** [A microscopic analysis of shear acceleration in the relativistic regime](https://arxiv.org/abs/2610.36867v1)
  - *本文从微观角度探讨了相对论性喷流中剪切加速的粒子动力学过程。*
- **[3]** [Revealing the companion of NGC 1850-BH1](https://arxiv.org/abs/2610.37262v1)
  - *通过多历元光谱分析，揭示了NGC 1850-BH1系统并非黑洞双星，而是一个由膨胀供体星和快速旋转伴星组成的系统。*
- **[3]** [Probing the inner disk edge of rotating neutron stars with dipole excitations in finite nuclei](https://arxiv.org/abs/2610.37394v1)
  - *本文探讨了利用原子核电偶极极化率约束中子星状态方程及内吸积盘轨道性质的方法。*
- **[3]** [Faint and Fast Transients from Double Detonations of Low Mass White Dwarfs](https://arxiv.org/abs/2610.37507v1)
  - *该论文利用数值模拟预测了低质量白矮星双爆轰产生的暗弱且快速的暂现源，探讨其作为新型超新星的可能性。*
- **[3]** [Effects of Dust in Electron-Capture Supernovae: Difficulty in Explaining Intermediate Luminosity Red Transients](https://arxiv.org/abs/2610.37574v1)
  - *通过半解析模型研究电子俘获超新星的尘埃效应，探讨其作为中等光度红暂现源（ILRTs）前身星的可行性。*
- **[3]** [Confirming candidate self-lensing binary detections with radial velocity measurements](https://arxiv.org/abs/2610.30203v2)
  - *该论文研究了通过径向速度测量结合光变曲线来确认和表征自透镜双星候选体的方法。*
- **[2]** [How Common Are Common Envelopes? Quantifying Their Role in Forming Gravitational-Wave Sources](https://arxiv.org/abs/2606.05322v2)
  - *该论文通过人口合成模拟研究了共同包层演化在引力波源形成中的作用，指出合并率测量本身无法唯一约束演化路径。*
- **[1]** [DUETS II - Red giant asteroseismic binaries. Binary confirmation and prospects for double-seismic model inference](https://arxiv.org/abs/2610.36209v1)
  - *该论文研究了红巨星日震双星的证实与双星地震学模型推断，与课题组的吸积盘、喷流或高能暂现源等核心研究领域不匹配。*
- **[1]** [Dynamical plausibility of triple-assisted interaction in Be-star multiple systems](https://arxiv.org/abs/2610.36304v1)
  - *研究利用动力学模拟探讨Be星多星系统中的三体辅助相互作用，分析Kozai-Lidov效应在内双星演化中的作用。*
- **[1]** [Periodic radio emission from a rapidly rotating T8 ultracool dwarf](https://arxiv.org/abs/2610.36336v1)
  - *本文报道了对超冷矮星WISE J1517+05的周期性射电爆发探测及其磁层物理机制研究。*
- **[1]** [Coherent Radio Emission from Flux Rope Mergers in 3D Relativistic Reconnection](https://arxiv.org/abs/2610.37214v1)
  - *本文利用三维相对论重联的粒子模拟研究了磁通量绳合并产生的相干无线电辐射。*
- **[1]** [The dearth of dustless HdC stars in the Magellanic Clouds: A metallicity-driven white dwarf merger mass effect](https://arxiv.org/abs/2610.37404v1)
  - *本文发现了麦哲伦星云中的前两颗无尘氢增丰碳星，并探讨其由白矮星并合形成的金属丰度依赖机制。*
- **[1]** [A Quiet Night in the Millihertz Sky? LISA Forecasts from LIGO/Virgo/KAGRA Populations](https://arxiv.org/abs/2610.37617v1)
  - *利用LIGO/Virgo/KAGRA的观测数据对LISA探测空间引力波黑洞双星事件进行了预测。*
- **[1]** [Semi-agnostic inspiral modeling: the massless scalar case at leading post-Newtonian order](https://arxiv.org/abs/2610.36037v1)
  - *该论文提出了超越广义相对论的黑洞双星旋进半不可知建模框架，重点研究无质量标量场与度规的耦合。*
- **[1]** [A Model to Map Brown Dwarf Companions to White Dwarfs in Partial Secondary Eclipse](https://arxiv.org/abs/2610.36141v1)
  - *该论文提出了一种利用凌星掩食和本征映射方法研究白矮星-褐矮星双星系统的大气结构的模型。*
- **[1]** [A Collimated Protostellar Outflow Likely Driven by Jet and Reshaped by Environment in the Sagittarius C Cloud of the Central Molecular Zone](https://arxiv.org/abs/2610.36573v1)
  - *利用ALMA和JWST联合观测分析了银心中央分子带Sgr C中一个准直原恒星外流的物理性质。*
- **[1]** [Searches for new particle physics by methods of classical and neutrino astronomy](https://arxiv.org/abs/2610.37198v1)
  - *该论文综述了利用天体物理方法和中微子天文手段来探寻新粒子物理的进展。*
- **[1]** [Nonthermal Particle Acceleration by Magnetic Pumping in Pulsating Plasmas](https://arxiv.org/abs/2606.05286v2)
  - *利用动理学模拟研究了脉动等离子体中磁泵浦机制对非热粒子的加速作用。*
- **[1]** [WFST Follow-up of S251112cm: Searching for an Optical Counterpart to a Subsolar-mass Compact-binary Merger Candidate](https://arxiv.org/abs/2609.18523v2)
  - *本文利用WFST对引力波事件S251112cm开展了光学对应体搜寻，排除了类千新星起源并约束了抛射物质量。*
- **[1]** [The youth of the intracluster medium. I. A non-parametric characterisation of the gas and electron number density profiles of $z \simeq 2$ protoclusters](https://arxiv.org/abs/2607.02654v2)
  - *本文利用数值模拟研究了z=2处原星系团中星系团际介质的气体质量与电子数密度分布。*
- **[1]** [Exceptional points and hysteresis in Kerr-Newman quasi-normal modes](https://arxiv.org/abs/2610.30049v2)
  - *本文研究了Kerr-Newman黑洞准正则模谱中的奇点与本征态迟滞现象。*
- **[0]** [CROMA: a GPU-accelerated Fokker--Planck solver for modeling non-thermal emission in post-processing cosmological simulations](https://arxiv.org/abs/2610.36074v1)
  - *本文介绍了一种用于宇宙学模拟中非热辐射建模的GPU加速Fokker-Planck求解器CROMA。*
- **[0]** [Testing Pre-main-sequence Evolutionary Models with Gaia and SPHEREx Observations of Canis Major North](https://arxiv.org/abs/2610.36223v1)
  - *利用Gaia和SPHEREx观测检验主前恒星演化模型。*
- **[0]** [Calculation of distant retrograde orbits and their use in space weather forecasting](https://arxiv.org/abs/2610.36315v1)
  - *该论文研究了日地远距离逆行轨道（DRO）及其在空间天气预报中的应用。*
- **[0]** [Heating of Solar Coronal Loops by Converging Unipolar Magnetic Flux: Evidence from SDO Observations and a Radiative MHD Simulation](https://arxiv.org/abs/2610.36362v1)
  - *本文利用SDO观测和磁流体动力学模拟研究了太阳日冕环的加热机制，与课题组黑洞、AGN及暂现源等研究领域无关。*
- **[0]** [Three-dimensional Magnetohydrodynamic Shocks and Associated Plasma Heating in the Solar Atmosphere](https://arxiv.org/abs/2610.36932v1)
  - *本文利用三维磁流体力学模拟研究了太阳大气中MHD激波的形成演化及等离子体加热机制。*
- **[0]** [The Clouds in the "Middle Ages" I. Star formation history and chemical abundances in the LMC](https://arxiv.org/abs/2610.37385v1)
  - *本文利用Gaia、OGLE和APOGEE数据研究大麦哲伦星系（LMC）中渐近巨支星（AGB）的恒星形成历史与化学丰度。*
- **[0]** [Absence of Magnetic Suppression in Massive Star Variability](https://arxiv.org/abs/2610.37495v1)
  - *该论文研究了大质量恒星中随机低频变源的磁场抑制效应，挑战了内重力波作为其普遍起因的假说。*
- **[0]** [Phase-Twist Instability in a Coprecessing Neutrino Plasma](https://arxiv.org/abs/2610.36101v1)
  - *本文研究了密集电子俘获超新星中微子等离子体中亚稳态共进动解位相扭曲不稳定性。*
- **[0]** [On the Interpretation of Tests of the Horizon Area Law](https://arxiv.org/abs/2610.36162v1)
  - *本文探讨了引力波视界面积定律检验的模型依赖性，并指出奇异致密星体可以模拟黑洞并通过该检验。*
- **[0]** [Quark Saturation in Magnetized Pure Neutron Matter](https://arxiv.org/abs/2610.36316v1)
  - *本文研究了磁场对纯中子物质中夸克饱和现象的影响及其密度依赖性。*
- **[0]** [Revisiting the Photometric Modulation Amplitudes of Kepler Planet Hosts: A Confounder-Adjusted Test of Stellar Spin-Orbit Alignment](https://arxiv.org/abs/2610.36664v1)
  - *该论文重新评估了Kepler行星宿主星的光度调制振幅与恒星自转-轨道对齐的关系，消除了视星等和半径等混淆变量的影响。*
- **[0]** [Quasiparticle Modeling of Strange Quark Stars with In-Medium QCD Effects at Finite Temperature and Strong Magnetic Fields](https://arxiv.org/abs/2610.36953v1)
  - *本文利用介质中QCD效应和准粒子模型研究了奇异夸克星的性质及状态方程。*
- **[0]** [FLITS: an interactive, reproducible workbench for fast radio burst analysis](https://arxiv.org/abs/2610.37034v1)
  - *本文介绍了用于快速射电暴（FRB）分析的开源Python软件包FLITS。*
- **[0]** [Quasinormal Ringing of a Schwarzschild Black Hole Surrounded by a King Dark Matter Halo: Higher-Order WKB Analysis](https://arxiv.org/abs/2610.37501v1)
  - *本文利用WKB方法研究了包围在King暗物质晕中的史瓦西黑洞的准正则振铃与微扰性质。*
- **[0]** [Weighing dark matter particles with gravitational waves](https://arxiv.org/abs/2610.37638v1)
  - *利用LISA空间引力波探测器观测极端质量比旋进（EMRI），通过波依赖的吸积和动力学摩擦效应测量超轻暗物质粒子的质量。*
- **[0]** [An autoencoder-based surrogate waveform model for quasi-circular binary-black-hole mergers](https://arxiv.org/abs/2602.00203v2)
  - *本文提出了一种基于自动编码器的双黑洞合并引力波快速波形替代模型AESur3dq8。*
- **[0]** [Relativistic Chiral MHD with application to the early Universe](https://arxiv.org/abs/2607.22816v2)
  - *本文推导了早期宇宙中相对论手征磁流体力学的方程，并探讨了其在辐射主导时期的磁场演化与手征发电机效应。*

[查看历史目录](./posts/index.md)
