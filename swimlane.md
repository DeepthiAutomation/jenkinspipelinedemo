flowchart LR

%% =========================
%% LEFT-ALIGNED SWIMLANES
%% =========================

subgraph DEV[Developer]
  A1[Intake requirement]
  A2[Build changes<br/>in Dev PREApproval]
  A3[Trigger Unpack]
end

subgraph PRS[PR Creation]
  A4[Raise PR Feature<br/>to Develop by Developer]
  A5[Raise PR Develop<br/>to Release by PodLead]
  A6[Raise PR Release<br/>to Main PreProd by Release Manager]
end

subgraph CI_PIPE[CI Pipelines]

  subgraph UNPACK[CI Unpack and Source Sync]
    B1[Export solution<br/>from Dev]
    B2[Diff against<br/>Feature branch]
    B3[Apply delta<br/>using solution strategy]
    B4[Commit to<br/>Feature branch]
  end

  subgraph PACK[CI Pack and Dev Refresh]
    D1[Pack from<br/>Develop]
    D2[Publish artifacts<br/>managed and unmanaged]
    D3[Deploy unmanaged<br/>to Dev]
  end

end

subgraph GOV[Approvals]
  C1[Approval Feature to Develop<br/>by PodLead or Delivery Lead]
  C2[Approval SIT deploy<br/>by TestLead]
  C3[Approval Develop to Release<br/>by Delivery Lead or TestLead]
  C4[Approval Release to Main PreProd<br/>by Release Manager or Delivery Lead]
  C6[Approval Release to Main PreProd<br/>by PO or BA]
  C5[CR approvals and<br/>Release Manager signoff]
end

subgraph CD_PIPE[CD Pipeline]

  subgraph SIT[SIT Validate]
    E1[Deploy unmanaged<br/>to SIT]
    E2[Run regression<br/>suite]
    E3[TestLead<br/>signoff]
  end

  subgraph UAT[UAT Validate]
    F1[Deploy managed<br/>to UAT]
    F2[Business<br/>signoff]
  end

  subgraph PREPROD[PreProd Validate]
    G1[Deploy managed<br/>to PreProd]
    G2[Run smoke<br/>and sanity]
    G3[PreProd<br/>signoff]
  end

  subgraph PROD[Production Release]
    H1[Deploy managed<br/>to Prod]
  end

end

%% =========================
%% MERGE CONFLICT RESOLUTION
%% =========================

G0[Resolve merge conflicts<br/>by Developer]

%% =========================
%% SEQUENTIAL FLOW
%% =========================

A1 --> A2 --> A3
A3 --> B1 --> B2 --> B3 --> B4 --> A4 --> G0 --> C1 --> D1 --> D2 --> D3
D3 --> C2 --> E1 --> E2 --> E3 --> A5 --> C3 --> F1 --> F2
F2 --> A6 --> C4 --> C6 --> G1 --> G2 --> G3 --> C5 --> H1
