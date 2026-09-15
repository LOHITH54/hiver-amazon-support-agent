# \# Hiver SDE Intern — AmazonHelp AI Support Agent

# 

# An AI support agent built using the Customer Support on Twitter dataset.

# 

# The system:

# 1\. Classifies an incoming customer message into a small set of support intents.

# 2\. Retrieves similar historical AmazonHelp cases and their support replies.

# 3\. Drafts a response grounded in those historical resolutions.

# 4\. Decides whether to auto-handle the request or escalate it to a human, with a reason.

# 

# \## 1. Problem Framing

# 

# Customer-support automation has two separate risks:

# 

# \- \*\*Intent risk:\*\* misunderstanding what the customer needs.

# \- \*\*Response risk:\*\* giving an answer that is not supported by historical evidence or requires account-specific investigation.

# 

# This project therefore separates classification, historical evidence retrieval, response drafting, and escalation.

# 

# \### Brand

# 

# \*\*AmazonHelp\*\*

# 

# AmazonHelp was selected because it has substantial support volume and many customer follow-up interactions, providing useful historical resolution evidence.

# 

# \### Intent taxonomy

# 

# The system uses eight top-level intents:

# 

# \- `delivery\_issue`

# \- `order\_issue`

# \- `refund\_return`

# \- `payment\_billing`

# \- `account\_access`

# \- `prime\_membership`

# \- `product\_issue`

# \- `other`

# 

# Cancellation and replacement are treated as subcases of broader intents rather than separate categories because they were relatively sparse.

# 

# \## 2. System Architecture

# 

# ```text

# Customer message

# &#x20;     |

# &#x20;     v

# Intent classifier

# (TF-IDF + Logistic Regression)

# &#x20;     |

# &#x20;     +--------------------+

# &#x20;     |                    |

# &#x20;     v                    v

# Confidence            Historical retrieval

# check                 similar AmazonHelp cases

# &#x20;                          |

# &#x20;                          v

# &#x20;                   Historical support replies

# &#x20;                          |

# &#x20;                          v

# &#x20;                   Grounded reply draft

# &#x20;                          |

# &#x20;                          v

# &#x20;                   Escalation decision

# &#x20;                          |

# &#x20;                +---------+---------+

# &#x20;                |                   |

# &#x20;             AUTO-HANDLE          ESCALATE

