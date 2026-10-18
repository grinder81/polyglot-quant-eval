# Ten-question pilot: complete question and answer review

These are likelihood-selected choices, not generated explanations. All three models selected the same answer on all ten items. Full vLLM scores are in ten-question/vllm-accuracy-small.json. Text below is reproduced from the saved dataset records, including original spelling.

## eng_Latn — dataset row 92

**Passage**

Unlike other primates, hominids no longer use their hands in locomotion or bearing weight or swinging through the trees. The chimpanzee's hand and foot are similar in size and length, reflecting the hand's use for bearing weight in knuckle walking. The human hand is shorter than the foot, with straighter phalanges. Fossil hand bones two million to three million years old reveal this shift in specialization of the hand from locomotion to manipulation.

**Question:** Which of the following accurately describes the phalanges of a chimpanzee? 

- **A:** They are straighter than a humans’
- **B:** Their hands and feet differ in size
- **C:** They are used for bearing weight
- **D:** They are used primarily for manipulation

**Correct answer: C — They are used for bearing weight**

| Model | Selected answer | Result |
|---|---|---|
| BF16 GGUF | A — They are straighter than a humans’ | Wrong |
| Four-bit GGUF | A — They are straighter than a humans’ | Wrong |
| Original BF16 / vLLM | Same selected answer as both GGUF models | Same correctness |

Candidate log-likelihoods (larger is preferred; not confidence percentages):

| Choice | BF16 | Four-bit |
|---|---:|---:|
| A | -0.259797 | -0.132617 |
| B | -2.118647 | -2.918556 |
| C | -2.526438 | -3.424060 |
| D | -4.542180 | -4.400758 |

Passage source: https://en.wikibooks.org/wiki/Introduction_to_Paleoanthropology/Bones

## eng_Latn — dataset row 877

**Passage**

"According to Ansa, ""police were concerned by a couple of top-level hits they feared might spark a full-blown war of succession. Police said Lo Piccolo had the upper hand because he had been Provenzano's right-hand man in Palermo and his greater experience won him the respect of the older generation of bosses as they pursued Provenzano's policy of keeping as low as possible while strengthening their power network. These bosses had been reined in by Provenzano when he put an end to the Riina-driven war against the state that claimed the lives of Mafia crusaders Giovanni Falcone and Paolo Borsellino in 1992."""

**Question:** Based on the information given in the passage, what was the cause of Falcone’s death?

- **A:** He was killed during the Riina-driven war
- **B:** He was killed by the police
- **C:** Lo Piccolo was ordered to kill him
- **D:** He was killed by fellow Mafia crusader Paolo Borsellino

**Correct answer: A — He was killed during the Riina-driven war**

| Model | Selected answer | Result |
|---|---|---|
| BF16 GGUF | A — He was killed during the Riina-driven war | Correct |
| Four-bit GGUF | A — He was killed during the Riina-driven war | Correct |
| Original BF16 / vLLM | Same selected answer as both GGUF models | Same correctness |

Candidate log-likelihoods (larger is preferred; not confidence percentages):

| Choice | BF16 | Four-bit |
|---|---:|---:|
| A | -0.148946 | -0.871675 |
| B | -5.261030 | -3.811597 |
| C | -6.482713 | -5.746367 |
| D | -3.712024 | -3.695184 |

Passage source: https://en.wikinews.org/wiki/Italy_arrests_reputed_Mafia_boss_Lo_Piccolo

## eng_Latn — dataset row 443

**Passage**

Registration is an additional requirement for the visa process. In some countries, you must register your presence and address where you are staying with the local authorities. This might require filling out a form with the local police or a visit to the immigration offices. In many countries with such a law, local hotels will handle the registration (make sure to ask). In other cases, only those staying outside of tourist accommodations need to register.  However, this makes the law much more obscure, so find out beforehand.

**Question:** Based on the passage, which statement regarding the registration requirement for the visa process is not true?

- **A:** If you’re staying in tourist accommodations, you might not need to register
- **B:** All countries require registration with the local authorities
- **C:** A visit to immigration offices might be required
- **D:** In some places, local hotels can handle the registration

**Correct answer: B — All countries require registration with the local authorities**

| Model | Selected answer | Result |
|---|---|---|
| BF16 GGUF | B — All countries require registration with the local authorities | Correct |
| Four-bit GGUF | B — All countries require registration with the local authorities | Correct |
| Original BF16 / vLLM | Same selected answer as both GGUF models | Same correctness |

Candidate log-likelihoods (larger is preferred; not confidence percentages):

| Choice | BF16 | Four-bit |
|---|---:|---:|
| A | -0.954098 | -1.754477 |
| B | -0.592543 | -0.321866 |
| C | -5.774941 | -5.711768 |
| D | -5.821043 | -5.202350 |

Passage source: https://en.wikivoyage.org/wiki/Visa

## ben_Beng — dataset row 382

**Passage**

"""আনসার মতে, """"পুলিশ শীর্ষ স্তরের বেশ কয়েকটি অভিঘাতের ব্যাপারে উদ্বিগ্ন ছিল ও তারা আশঙ্কা করেছিল যে উত্তরাধিকারের জন্য একটি সম্পূর্ণ যুদ্ধের সূচনা হতে পারে।"" পুলিশ জানিয়েছে লো পিকোলোর জন্য সুবিধা ছিল বেশি কারণ তিনি পালের্মোতে প্রোভেনজানোর ডান হাত ছিলেন এবং তার বৃহত্তর অভিজ্ঞতার কারণে তিনি তার প্রবীণ প্রজন্মের কর্তাদের সম্মান অর্জন করেছিলেন, যারা আড়ালে থেকে নিজের শক্তি বাড়ানোর ব্যাপারে প্রোভেনজানোর নীতি অনুসরণ করতেন। 1992 সালে রাষ্ট্রের বিরুদ্ধে রিনা পরিচালিত বিদ্রোহের অবসান ঘটিয়েছিলেন প্রভেনজানো। এই সময়েই মাফিয়া ক্রুসেডার ডিওভানি ফ্যালকন এবং পাওনলো বোর্সেলিনোর মৃত্যু হয়। এই প্রভেনজানোরই এই কর্তাব্যক্তিদের নিয়ন্ত্রণে রাখতেন।"

**Question:** অনুচ্ছেদে দেওয়া তথ্যের ভিত্তিতে, ফ্যালকোনের মৃত্যুর কারণ কী ছিল?

- **A:** রিনা পরিচালিত বিদ্রোহের সময় তাকে মারা হয়েছিল
- **B:** পুলিশের গুলিতে সে মারা গিয়েছিল
- **C:** লো পিকোলো তাকে মারার আদেশ দিয়েছিল
- **D:** সে তার সহ মাফিয়া ক্রুসেডার পাওলো বোরসেলিনোর হাতে মারা গিয়েছিল

**Correct answer: A — রিনা পরিচালিত বিদ্রোহের সময় তাকে মারা হয়েছিল**

| Model | Selected answer | Result |
|---|---|---|
| BF16 GGUF | A — রিনা পরিচালিত বিদ্রোহের সময় তাকে মারা হয়েছিল | Correct |
| Four-bit GGUF | A — রিনা পরিচালিত বিদ্রোহের সময় তাকে মারা হয়েছিল | Correct |
| Original BF16 / vLLM | Same selected answer as both GGUF models | Same correctness |

Candidate log-likelihoods (larger is preferred; not confidence percentages):

| Choice | BF16 | Four-bit |
|---|---:|---:|
| A | -0.012512 | -0.020228 |
| B | -5.408176 | -5.105431 |
| C | -6.535514 | -6.182026 |
| D | -6.018051 | -5.677775 |

Passage source: https://en.wikinews.org/wiki/Italy_arrests_reputed_Mafia_boss_Lo_Piccolo

## ben_Beng — dataset row 877

**Passage**

মঙ্গলবার  ম্যাসাচুসেটস এর প্রাক্তন গভর্নর মিট রম্নি ফ্লরিডায় অনুষ্ঠিত রিপাবলিকান পার্টির রাষ্ট্রপতি পদপ্রার্থী নির্ধারণের প্রাইমারি নির্বাচন  46 শতাংশের বেশি ভোট পেয়ে জিতেছেন। হাউসের সাবেক মার্কিন স্পিকার নিউট জিঙ্গরিচ ৩২ শতাংশ ভোট নিয়ে দ্বিতীয় স্থানে এসেছেন। সমস্ত রাজ্যে বিজয়ী হিসাবে, ফ্লোরিডা তার পঞ্চাশটি প্রতিনিধির সবকটি দিয়ে রোমনিকে পুরস্কৃত করেছিল, তাকে রিপাবলিকান পার্টির মনোনয়নের জন্য নেতৃত্বকারী হিসাবে এগিয়ে নিয়ে এসেছিল।

**Question:** সমস্ত রাজ্যে বিজয়ী হিসাবে ফ্লোরিডার মর্যাদার কারণে, মিট রম্নি কোন পুরস্কারে পুরস্কৃত হয়েছেন?

- **A:** রাজ্যের প্রতিনিধির মধ্যে 32 জন
- **B:** রিপাবলিকান পার্টির মনোনয়ন
- **C:** রাজ্যের সমস্ত প্রতিনিধি
- **D:** 46 শতাংশ ভোট

**Correct answer: C — রাজ্যের সমস্ত প্রতিনিধি**

| Model | Selected answer | Result |
|---|---|---|
| BF16 GGUF | B — রিপাবলিকান পার্টির মনোনয়ন | Wrong |
| Four-bit GGUF | B — রিপাবলিকান পার্টির মনোনয়ন | Wrong |
| Original BF16 / vLLM | Same selected answer as both GGUF models | Same correctness |

Candidate log-likelihoods (larger is preferred; not confidence percentages):

| Choice | BF16 | Four-bit |
|---|---:|---:|
| A | -6.212663 | -5.910186 |
| B | -0.519583 | -0.090024 |
| C | -0.953153 | -2.595248 |
| D | -8.687617 | -7.404315 |

Passage source: https://en.wikinews.org/wiki/Mitt_Romney_wins_2012_Florida_primary

## ben_Beng — dataset row 153

**Passage**

অন্যান্য স্তন্যপায়ীদের মতো হোমিনিডরা এখন আর তাদের হাতকে চলাফেরা বা ওজন বহন বা গাছ থেকে গাছে ঝুলে ঝুলে যাওয়ার জন্য ব্যবহার করে না। শিম্পাঞ্জির হাত ও পায়ের আকার এবং দৈর্ঘ্য সমান, গিঁট হাঁটার সময় ওজন বহন করার জন্য হাতের ব্যবহার প্রতিফলিত করে। স্ট্রেইটার ফ্যালঞ্জস নিয়েও মানুষের হাত পায়ের চেয়ে ছোট। 20 ‌লক্ষ থেকে 30 লক্ষ বছরের পুরনো হাতের হাড়ের ফসিলগুলি প্রমাণ করছে যে কীভাবে হাতের বিবর্তন গতিশক্তি থেকে দক্ষতায় রূপান্তরিত হয়েছে।

**Question:** এর মধ্যে কোনটি শিম্পাঞ্জির আঙ্গুলের হাড় নির্ভুলভাবে বর্ণনা করে? 

- **A:** এগুলি মানুষের থেকে সোজা আকৃতির হয়
- **B:** তাদের হাত এবং পায়ের আকার আলাদা
- **C:** এগুলি ওজন তোলার কাজে ব্যবহৃত হয়
- **D:** মূলত হাতের সাহায্যে কিছু নিয়ন্ত্রণ করতে এগুলি ব্যবহার করা হয়

**Correct answer: C — এগুলি ওজন তোলার কাজে ব্যবহৃত হয়**

| Model | Selected answer | Result |
|---|---|---|
| BF16 GGUF | A — এগুলি মানুষের থেকে সোজা আকৃতির হয় | Wrong |
| Four-bit GGUF | A — এগুলি মানুষের থেকে সোজা আকৃতির হয় | Wrong |
| Original BF16 / vLLM | Same selected answer as both GGUF models | Same correctness |

Candidate log-likelihoods (larger is preferred; not confidence percentages):

| Choice | BF16 | Four-bit |
|---|---:|---:|
| A | -0.631861 | -1.024983 |
| B | -2.010769 | -1.673674 |
| C | -1.507900 | -1.351519 |
| D | -3.284088 | -2.636598 |

Passage source: https://en.wikibooks.org/wiki/Introduction_to_Paleoanthropology/Bones

## ben_Beng — dataset row 184

**Passage**

ভিসা প্রক্রিয়ার জন্য রেজিস্ট্রেশন একটি অতিরিক্ত প্রয়োজনীয়তা। কিছু দেশে, আপনার উপস্থিতি এবং ঠিকানা নিবন্ধন অবশ্যই করতে হবে যেখানে আপনি স্থানীয় কর্তৃপক্ষের সাথে আছেন। এর জন্য স্থানীয় পুলিশদের কাছে একটি ফর্ম পূরণ করে জমা দেওয়া বা অভিবাসন দফতরে পরিদর্শন করার প্রয়োজন হতে পারে। এই আইন আছে এমন অনেক দেশে, স্থানীয় হোটেলগুলি নিবন্ধীকরণ করতে হবে (অবশ্যই জিজ্ঞেস করে নিতে হবে) অন্যান্য ক্ষেত্রে, কেবলমাত্র পর্যটন আবাসনের বাইরে থাকা ব্যক্তিদের রেজিস্টার করার দরকার হয়। যাইহোক এটি আইনটিকে আরও বেশি অস্পষ্ট করে তোলে, তাই আগেভাগেই খুঁজে বার করুন।

**Question:** অনুচ্ছেদটির ভিত্তিতে, ভিসা প্রক্রিয়ার জন্য রেজিস্ট্রেশনের প্রয়োজনীয়তা সংক্রান্ত কোন বিবৃতিটি সত্য নয়?

- **A:** আপনি যদি পর্যটন আবাসনে থাকেন, তাহলে আপনার নিবন্ধন করার প্রয়োজন নাও থাকতে পারে
- **B:** সমস্ত দেশেই স্থানীয় কর্তৃপক্ষের নিকটে নিবন্ধন করা প্রয়োজন
- **C:** অভিবাসন দফতরে যাওয়ার প্রয়োজন হতে পারে
- **D:** কয়েকটি জায়গায় স্থানীয় হোটেলের তরফে নিবন্ধন করানো হয়

**Correct answer: B — সমস্ত দেশেই স্থানীয় কর্তৃপক্ষের নিকটে নিবন্ধন করা প্রয়োজন**

| Model | Selected answer | Result |
|---|---|---|
| BF16 GGUF | A — আপনি যদি পর্যটন আবাসনে থাকেন, তাহলে আপনার নিবন্ধন করার প্রয়োজন নাও থাকতে পারে | Wrong |
| Four-bit GGUF | A — আপনি যদি পর্যটন আবাসনে থাকেন, তাহলে আপনার নিবন্ধন করার প্রয়োজন নাও থাকতে পারে | Wrong |
| Original BF16 / vLLM | Same selected answer as both GGUF models | Same correctness |

Candidate log-likelihoods (larger is preferred; not confidence percentages):

| Choice | BF16 | Four-bit |
|---|---:|---:|
| A | -0.225827 | -0.853454 |
| B | -2.294698 | -1.040393 |
| C | -4.939652 | -4.886425 |
| D | -5.558612 | -5.001777 |

Passage source: https://en.wikivoyage.org/wiki/Visa

## hin_Deva — dataset row 92

**Passage**

अन्य नरवानर गण के विपरीत, वनमानुष अब अपने हाथों का इस्तेमाल चलने में या वज़न उठाने या पेड़ों से झूलने में नहीं करते हैं. चिंपांजी का हाथ और पैर आकार और लंबाई में समान होते हैं, जो घुटनों के बल चलने में भार वहन करने के लिए हाथ के उपयोग को दर्शाता है. सीधी फलांगों के साथ मनुष्य का हाथ उसके पैर से छोटा होता है. जीवाश्म के हाथ की हड्डियाँ दो मिलियन से तीन मिलियन साल पुरानी हैं, यह हाथ की विशेषज्ञता को लोकोमोशन से मैनिपुलेशन तक बदलने के बारे में बताती हैं.

**Question:** निम्नलिखित में से कौन सा एक चिंपांज़ी की उंगली की हड्डियों का सटीक वर्णन करता है?

- **A:** वे मनुष्यों की तुलना में सीधे हैं’
- **B:** उनके हाथ और पैर आकार में भिन्न होते हैं
- **C:** उनका उपयोग वजन सहन करने के लिए किया जाता है
- **D:** वे मुख्य रूप से हेरफेर के लिए उपयोग किए जाते हैं

**Correct answer: C — उनका उपयोग वजन सहन करने के लिए किया जाता है**

| Model | Selected answer | Result |
|---|---|---|
| BF16 GGUF | A — वे मनुष्यों की तुलना में सीधे हैं’ | Wrong |
| Four-bit GGUF | A — वे मनुष्यों की तुलना में सीधे हैं’ | Wrong |
| Original BF16 / vLLM | Same selected answer as both GGUF models | Same correctness |

Candidate log-likelihoods (larger is preferred; not confidence percentages):

| Choice | BF16 | Four-bit |
|---|---:|---:|
| A | -0.605237 | -0.806473 |
| B | -3.658151 | -2.939977 |
| C | -2.891338 | -2.724947 |
| D | -1.157183 | -1.097216 |

Passage source: https://en.wikibooks.org/wiki/Introduction_to_Paleoanthropology/Bones

## hin_Deva — dataset row 521

**Passage**

अन्सा के अनुसार, “पुलिस शीर्ष स्तर के कुछ हिट्स से चिंतित थी उन्हें डर था कि वे उत्तराधिकार के लिए एक जंग छेड़ सकते हैं. पुलिस ने कहा कि लो पिकालो की स्थिति मज़बूत थी क्योंकि वह पलेर्मो में प्रोवेनज़ानो का दाहिना हाथ था और उसके अनुभव ने उसे पुरानी पीढ़ी के मालिकों का सम्मान दिलवाया था क्योंकि वे अपने शक्ति तंत्र को मजबूत करते हुए अपनी छवि को न्यून बनाए रखने के प्रोवेनज़ानो की नीति का अनुसरण करते थे। इन मालिकों को प्रोवेनज़ानो ने अपने वश में कर रखा था जब उन्होंने 1992 में राज्य के विरुद्ध रीना-द्वारा संचालित युद्ध को समाप्त किया जिसमें माफिया योद्धा जियोवानी फैल्कोन और पाओलो बोरसेलिनो की जान चली गई थी।”

**Question:** गद्यांश में दी गई जानकारी के आधार पर फैल्कोन की मृत्यु का कारण क्या था?

- **A:** वह रीना द्वारा संचालित युद्ध के दौरान मारा गया था
- **B:** उसे पुलिस ने मार गिराया
- **C:** लो पिकालो को उसे मारने का आदेश दिया गया था
- **D:** वह साथी माफिया क्रूसेडर पाओलो बोरसेलिनो द्वारा मारा गया था

**Correct answer: A — वह रीना द्वारा संचालित युद्ध के दौरान मारा गया था**

| Model | Selected answer | Result |
|---|---|---|
| BF16 GGUF | A — वह रीना द्वारा संचालित युद्ध के दौरान मारा गया था | Correct |
| Four-bit GGUF | A — वह रीना द्वारा संचालित युद्ध के दौरान मारा गया था | Correct |
| Original BF16 / vLLM | Same selected answer as both GGUF models | Same correctness |

Candidate log-likelihoods (larger is preferred; not confidence percentages):

| Choice | BF16 | Four-bit |
|---|---:|---:|
| A | -0.043460 | -0.243757 |
| B | -6.306171 | -5.175028 |
| C | -6.034527 | -5.214785 |
| D | -4.907154 | -4.160017 |

Passage source: https://en.wikinews.org/wiki/Italy_arrests_reputed_Mafia_boss_Lo_Piccolo

## hin_Deva — dataset row 443

**Passage**

वीजा प्रक्रिया के लिए पंजीकरण एक अतिरिक्त आवश्यकता है. कुछ देशों में, आपको अपनी उपस्थिति और पता पंजीकृत करना होगा जहाँ आप स्थानीय अधिकारियों के साथ रह रहे हैं. इसके लिए स्थानीय पुलिस के पास एक फॉर्म भरने की या आप्रवासन कार्यालयों में जाने आवश्यकता पड़ सकती है। इस तरह के कानून वाले कई देशों में, स्थानीय होटल पंजीकरण संभाल लेंगे (पूछना सुनिश्चित करें). दूसरे मामलों में, सिर्फ़ ऐसे लोगों को रजिस्टर करने की ज़रुरत है जो पर्यटकों के ठहरने की जगहों से अलग कहीं रुके हैं. हालाँकि, यह बात कानून को ज़्यादा अजीब बनाती है, इसलिए पहले ही जानकारी जुटा लें.

**Question:** परिच्छेद के आधार पर, वीजा प्रक्रिया के लिए पंजीकरण आवश्यकता के संबंध में कौन सा कथन सत्य नहीं है?

- **A:** अगर आप पर्यटकों के ठहरने की जगह में रहते हैं, तो आपको रजिस्ट्रेशन करने की ज़रूरत नहीं है
- **B:** सभी देशों में स्थानीय अधिकारियों के पास जाएं और पंजीकरण करें
- **C:** आप्रवासन कार्यालयों में जाना होगा
- **D:** कुछ स्थानों पर, स्थानीय होटल रिकॉर्ड को संभालेंगे

**Correct answer: B — सभी देशों में स्थानीय अधिकारियों के पास जाएं और पंजीकरण करें**

| Model | Selected answer | Result |
|---|---|---|
| BF16 GGUF | A — अगर आप पर्यटकों के ठहरने की जगह में रहते हैं, तो आपको रजिस्ट्रेशन करने की ज़रूरत नहीं है | Wrong |
| Four-bit GGUF | A — अगर आप पर्यटकों के ठहरने की जगह में रहते हैं, तो आपको रजिस्ट्रेशन करने की ज़रूरत नहीं है | Wrong |
| Original BF16 / vLLM | Same selected answer as both GGUF models | Same correctness |

Candidate log-likelihoods (larger is preferred; not confidence percentages):

| Choice | BF16 | Four-bit |
|---|---:|---:|
| A | -0.623574 | -0.791158 |
| B | -1.248752 | -1.446229 |
| C | -5.166147 | -5.322960 |
| D | -6.073153 | -5.485757 |

Passage source: https://en.wikivoyage.org/wiki/Visa
