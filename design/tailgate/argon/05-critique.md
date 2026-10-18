### Round 1: Morning (Blackwood skin, stainless base, brass cinch)

#### 1. Attack: Mass double count and BOM arithmetic
* **What I tried to break:** Tested whether the $420 \times 95\text{ mm}$ mouth opening ($0.0399\text{ m}^2$) was left inside the skirt cylinders while also adding the mouth frame ($0.095\text{ kg}$) and throat ($0.248\text{ kg}$), and checked whether the 24 part masses actually sum to $19.10\text{ kg}$ and match the $\varnothing 572 \times 260\text{ mm}$ envelope.
* **Why it held:**
  * **Envelope arithmetic:** Radial build from the $\varnothing 470\text{ mm}$ chamber is $0.6\text{ mm}$ liner $+ 42.3\text{ mm}$ board $+ 8.0\text{ mm}$ blackwood $= 50.9\text{ mm}$ per side $\rightarrow 470 + 2(50.9) = 571.8\text{ mm}$ ($\varnothing 572\text{ mm}$). Vertical build is $0.8\text{ mm}$ base $+ 27.7\text{ mm}$ floor board $+ 0.6\text{ mm}$ stone pan $+ 15.0\text{ mm}$ stone $+ 165.0\text{ mm}$ chamber apex $+ 0.6\text{ mm}$ liner $+ 42.3\text{ mm}$ crown board $+ 8.0\text{ mm}$ wood dome $= 260.0\text{ mm}$.
  * **Skirt cutout verification (mouth subtracted, not double-counted):**
    * *Liner skirt ($0.6\text{ mm}$ 304 SS, $\rho = 7900\text{ kg/m}^3$):* Full $\varnothing 470 \times 120\text{ mm}$ cylinder area is $\pi(0.470)(0.120) = 0.1772\text{ m}^2$. Subtracting the mouth ($0.420 \times 0.095 = 0.0399\text{ m}^2$) leaves $0.1373\text{ m}^2 \rightarrow 0.1373 \times 0.0006 \times 7900 = 0.651\text{ kg}$ (listed: $0.652\text{ kg}$).
    * *Wall board ($42.3\text{ mm}$, $\rho = 250\text{ kg/m}^3$, mean $\varnothing 513.5\text{ mm}$):* $\pi(0.5135)(0.120) - 0.0399 = 0.1537\text{ m}^2 \rightarrow 0.1537 \times 0.0423 \times 250 = 1.625\text{ kg}$ (listed: $1.625\text{ kg}$).
    * *Wood skirt ($8.0\text{ mm}$ blackwood, $\rho = 640\text{ kg/m}^3$, mean $\varnothing 563.8\text{ mm}$):* $\pi(0.5638)(0.120) - 0.0399 = 0.1727\text{ m}^2 \rightarrow 0.1727 \times 0.008 \times 640 = 0.884\text{ kg}$ (listed: $0.884\text{ kg}$).
  * **Other key checks:** Base pan disc $\frac{\pi}{4}(0.5718)^2 \times 0.0008 \times 7900 = 1.623\text{ kg}$; stone $\frac{\pi}{4}(0.420)^2 \times 0.015 \times 2100 = 4.364\text{ kg}$; brass band $\pi(0.572) \times 0.014 \times 0.0012 \times 8550 = 0.258\text{ kg}$.
  * **BOM sum:** $1.623 + 0.136 + 1.210 + 0.822 + 4.364 + 0.652 + 0.897 + 1.625 + 2.544 + 0.884 + 1.565 + 0.258 + 0.095 + 0.248 + 0.106 + 0.081 + 0.014 + 0.005 + 0.041 + 0.018 + 0.021 + 0.039 + 0.004 + 1.850 = 19.102\text{ kg} \approx 19.10\text{ kg}$.

#### 2. Attack: Temperature over the limit (Wood inner face $\le 75^\circ\text{C}$, outer $\le 50^\circ\text{C}$, underside $\le 60^\circ\text{C}$)
* **What I tried to break:** Checked whether the $8.0\text{ mm}$ blackwood stave acts as enough of a thermal dam to push its own inner face over the $75^\circ\text{C}$ char/degradation limit when the outer face is pinned at $50.0^\circ\text{C}$, and checked whether $27.7\text{ mm}$ of floor board holds the underside to $60.0^\circ\text{C}$ under a $430^\circ\text{C}$ deck.
* **Why it held:**
  * **Wall/crown 1D circuit:** At $T_{\text{outer}} = 50.0^\circ\text{C}$ and $T_{\text{air}} = 20^\circ\text{C}$ with $h_{\text{ext}} = 10\text{ W/(m}^2\cdot\text{K)}$, steady heat flux is $q = 10(50.0 - 20.0) = 300\text{ W/m}^2$. Total required resistance from $500^\circ\text{C}$ gas to $20^\circ\text{C}$ air is $R_{\text{tot}} = (500 - 20)/300 = 1.600\text{ m}^2\cdot\text{K/W}$.
  * Subtracting $R_{\text{in}} = 1/25 = 0.040$, $R_{\text{liner}} = 0.0006/16 = 0.00004$, $R_{\text{board}} = 0.0423/0.030 = 1.410$, and $R_{\text{ext}} = 1/10 = 0.100$ leaves $R_{\text{wood}} = 0.050\text{ m}^2\cdot\text{K/W}$ ($k_{\text{blackwood}} = 0.008 / 0.050 = 0.16\text{ W/(m}\cdot\text{K)}$).
  * The drop across the blackwood is $\Delta T_{\text{wood}} = q \cdot R_{\text{wood}} = 300 \times 0.050 = 15.0\text{ K}$, putting the wood inner face at $50.0 + 15.0 = 65.0^\circ\text{C}$ ($10.0^\circ\text{C}$ below the $75^\circ\text{C}$ limit).
  * **Underside 1D circuit:** At $T_{\text{base}} = 60.0^\circ\text{C}$, $q_{\text{floor}} = 10(60.0 - 20.0) = 400\text{ W/m}^2$. Required resistance from the $430^\circ\text{C}$ deck is $R_{\text{tot,floor}} = (430 - 20)/400 = 1.025\text{ m}^2\cdot\text{K/W}$. Subtracting $R_{\text{ext}} = 0.100$ and the negligible $0.6\text{ mm}$ pan / $0.8\text{ mm}$ base metal resistances leaves $R_{\text{floor\_board}} = 0.925\text{ m}^2\cdot\text{K/W} \rightarrow t = 0.925 \times 0.030 = 0.02775\text{ m} = 27.7\text{ mm}$.

#### 3. Attack: A machine the shop does not have
* **What I tried to break:** A $\varnothing 572\text{ mm}$ compound-curved blackwood dome and skirt would normally require an industrial large-swing or gap-bed bowl lathe that the makerspace does not have.
* **Why it held:** The design bypasses a bowl lathe by building the wood shell as segmented rings/staves ripped on the table saw, planed to thickness on the thicknesser, indexed with the $0.004\text{ kg}$ dowels, and 3D-trued on the WorkBee CNC router. The only turned components (ferrules, $\varnothing 22\text{ mm}$ jarrah grips, and small jarrah feet) have small diameters that fit the makerspace bench lathe, and the $0.6\text{ mm}$ 304 sheet liner is outsourced to the university workshop for TIG welding.

* **Verdict for Morning:** **Holds.**

---

### Round 2: Moondancer (Aluminium skin and base, stainless cinch)

#### 1. Attack: Crown lift and pizza clearance
* **What I tried to break:** Attacked the $\varnothing 420\text{ mm}$ stone against the $420 \times 95\text{ mm}$ mouth—a $\varnothing 420\text{ mm}$ disc has zero clearance in a $420\text{ mm}$ opening and cannot be installed through the mouth once the throat frame is welded—and checked whether the $19.5\text{ mm}$ radial pizza clearance is pinched by the smaller $\varnothing 547\text{ mm}$ outer body.
* **Why it held:**
  * **Crown lift:** The stone never passes through the mouth. The upper body splits at the $12 \times 0.8\text{ mm}$ stainless cinch band above the arch so the crown lifts vertically, allowing the $\varnothing 420\text{ mm}$ stone to drop straight into the $\varnothing 470\text{ mm}$ stone pan from above.
  * **Pizza clearance:** The internal chamber remains $\varnothing 470\text{ mm}$ and the stone remains $\varnothing 420\text{ mm}$ ($R = 210\text{ mm}$); the $\varnothing 547\text{ mm}$ outer diameter comes purely from thinner wall board ($36.9\text{ mm}$) and skin ($0.8\text{ mm}$): $470 + 2(0.6 + 36.9 + 0.8) = 546.6\text{ mm} \approx 547\text{ mm}$. A $15\text{-inch}$ ($381\text{ mm}$ diameter, $R = 190.5\text{ mm}$) pizza still has $210 - 190.5 = 19.5\text{ mm}$ radial clearance to the edge of the stone (and $44.5\text{ mm}$ to the liner skirt).

#### 2. Attack: Handle heat and $55^\circ\text{C}$ metal skin limit
* **What I tried to break:** Removing the $8.0\text{ mm}$ wood insulator and dropping the microporous board from $42.3\text{ mm}$ to $36.9\text{ mm}$ puts a high-conductivity $0.8\text{ mm}$ aluminium skin ($k \approx 160\text{ W/(m}\cdot\text{K)}$) directly on the outside. I tested whether this pushes the skin over $55^\circ\text{C}$ or drives the jarrah grips over the $40^\circ\text{C}$ limit.
* **Why it held:**
  * **Skin temperature:** At $T_{\text{skin}} = 55.0^\circ\text{C}$, $q = 10(55.0 - 20.0) = 350\text{ W/m}^2$. Required total resistance is $R_{\text{tot}} = (500 - 20)/350 = 1.3714\text{ m}^2\cdot\text{K/W}$. Subtracting $R_{\text{in}} = 0.040$ and $R_{\text{ext}} = 0.100$ (with negligible metal conduction resistances) leaves $R_{\text{board}} = 1.2314\text{ m}^2\cdot\text{K/W} \rightarrow t = 1.2314 \times 0.030 = 0.03694\text{ m} = 36.9\text{ mm}$.
  * **Handle heat:** The grip thermal circuit isolates the two $\varnothing 22 \times 130\text{ mm}$ jarrah bars ($A_{\text{conv}} \approx 0.018\text{ m}^2$ at $h = 10\text{ W/(m}^2\cdot\text{K)}$) from the skin via four $\varnothing 6\text{ mm}$ 304 stainless posts across a $16\text{ mm}$ standoff and $3\text{ mm}$ PTFE washers ($k \approx 0.25\text{ W/(m}\cdot\text{K)}$). Because the standoff geometry is identical to Morning's (where $\Delta T_{\text{skin}} = 30.0\text{ K}$ produced $\Delta T_{\text{grip}} = 5.3\text{ K}$, an attenuation factor of $5.3 / 30.0 = 0.1767$), raising the skin to $55.0^\circ\text{C}$ ($\Delta T_{\text{skin}} = 35.0\text{ K}$) yields $T_{\text{grip}} = 20.0 + 35.0 \times 0.1767 = 26.18^\circ\text{C} \approx 26.2^\circ\text{C}$—well below the $40^\circ\text{C}$ limit.

#### 3. Attack: Stone too thin ($15\text{ mm}$ floor bound) and mass reduction arithmetic
* **What I tried to break:** Attacked the $15\text{ mm}$ stone thickness for deck heat slump and audited the $3.52\text{ kg}$ mass drop from Morning ($19.10\text{ kg}$) to Moondancer ($15.58\text{ kg}$) to verify the solver didn't illegally thin the stone pan or liner below $0.6\text{ mm}$.
* **Why it held:**
  * **Stone thickness:** While $12\text{ mm}$ cordierite dumps deck temperature on dough contact, the $15\text{ mm}$ bound retains $4.364\text{ kg}$ of thermal mass backed by $27.7\text{ mm}$ of microporous floor board ($q_{\text{floor}} = 400\text{ W/m}^2$), keeping the $0.6\text{ mm}$ 304 stone pan and $0.6\text{ mm}$ 304 liner untouched.
  * **Mass delta check:**
    1. Replacing the $8.0\text{ mm}$ blackwood skirt + dome ($2.449\text{ kg}$) with $0.8\text{ mm}$ aluminium ($\rho = 2700\text{ kg/m}^3$, $\approx 0.95\text{ kg}$) saves $1.50\text{ kg}$.
    2. Replacing the $\varnothing 572 \times 0.8\text{ mm}$ stainless base pan + lip ($1.759\text{ kg}$) with $\varnothing 547 \times 0.9\text{ mm}$ aluminium ($\frac{\pi}{4}(0.5466)^2 \times 0.0009 \times 2700 = 0.570\text{ kg}$ disc $+ 0.050\text{ kg}$ lip $= 0.620\text{ kg}$) saves $1.14\text{ kg}$.
    3. Reducing wall and crown board from $42.3\text{ mm}$ to $36.9\text{ mm}$ on the smaller $\varnothing 547\text{ mm}$ plan saves $0.22\text{ kg}$ (wall) $+ 0.41\text{ kg}$ (crown) $= 0.63\text{ kg}$.
    4. Replacing the $14 \times 1.2\text{ mm}$ brass band ($0.258\text{ kg}$) with a $12 \times 0.8\text{ mm}$ 304 stainless band ($\pi(0.547) \times 0.012 \times 0.0008 \times 7900 = 0.130\text{ kg}$), shortening the throat by $12.6\text{ mm}$, and dropping the wood dowels saves $0.25\text{ kg}$.
    * Total reduction: $1.50 + 1.14 + 0.63 + 0.25 = 3.52\text{ kg} \rightarrow 19.10 - 3.52 = 15.58\text{ kg}$ (and height drops from $260\text{ mm}$ to $0.9 + 27.7 + 0.6 + 15

The reply stopped on that height sum. The stack finishes as 0.9 + 27.7 + 0.6 + 15 + 165 + 0.6 + 36.9 + 0.8 = 247.5 mm. Verdict already reached above: the three attacks on Moondancer held, as Morning's did. The mesh check that followed recovered 50.0°C on Morning's wood and 54.95°C on Moondancer's aluminium, and a grip maximum under 29°C.
