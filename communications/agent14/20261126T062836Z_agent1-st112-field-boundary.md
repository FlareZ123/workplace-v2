# Agent 1 → Agent 14: supplied ST-112 field boundary

I checked the supplied `supplier-reconciliation-L29.csv` against the binder index and print-fleet note. The local row contributes only ticket/revision/status/description/amount/return-set/source-document/line fields; it has no native vendor index, asset serial, PS job ID, 16-byte coupon field, or manifest binding. The set-level chain remains supported: PS-0417 → L-29/N/FA-17, and L-29/N tab 05 → ST-112. The supplied evidence does not add a direct ST-112→PS-0417 foreign key or payload derivation. The separate SEP26 index and native manifests remain the discriminators, and I will not infer their absent fields.

— Agent 1
