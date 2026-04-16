# Codebase Revision Plan for Parent Slide Count Implementation

## Phase 1: Core Config Updates (1-30)
1. state/config/experience-profiles.yaml: Add cluster_expansion.avg_interstitials_per_cluster: 3.0 under visual-led. Why: Avg expansion. Location: visual-led block. When: Phase 1.
2. state/config/experience-profiles.yaml: Add cluster_expansion.max_interstitials_per_cluster: 5 under visual-led. Why: Max cap. Location: visual-led.
3. state/config/experience-profiles.yaml: Add cluster_expansion.min_interstitials_per_cluster: 1 under visual-led. Why: Min. Location: visual-led.
4. state/config/experience-profiles.yaml: Add cluster_expansion.avg_interstitials_per_cluster: 2.0 under text-led. Why: Avg expansion. Location: text-led block.
5. state/config/experience-profiles.yaml: Add cluster_expansion.max_interstitials_per_cluster: 4 under text-led. Why: Max cap. Location: text-led.
6. state/config/experience-profiles.yaml: Add cluster_expansion.min_interstitials_per_cluster: 1 under text-led. Why: Min. Location: text-led.
7. state/config/experience-profiles.yaml: Add parent_slide_count_range.min: 5 under visual-led. Why: UX bounds. Location: visual-led.
8. state/config/experience-profiles.yaml: Add parent_slide_count_range.max: 12 under visual-led. Why: UX bounds. Location: visual-led.
9. state/config/experience-profiles.yaml: Add parent_slide_count_range.min: 8 under text-led. Why: UX bounds. Location: text-led.
10. state/config/experience-profiles.yaml: Add parent_slide_count_range.max: 15 under text-led. Why: UX bounds. Location: text-led.
11. state/config/experience-profiles.yaml: Add target_runtime_estimate.avg_slide_runtime: 45 under visual-led. Why: Timing. Location: visual-led.
12. state/config/experience-profiles.yaml: Add target_runtime_estimate.avg_slide_runtime: 60 under text-led. Why: Timing. Location: text-led.
13. state/config/experience-profiles.yaml: Update schema_version to "1.1". Why: Version. Location: top.
14. state/config/experience-profiles.yaml: Add comment "# Parent slide and cluster expansion controls". Why: Doc. Location: top.
15. state/config/experience-profiles.yaml: Validate YAML syntax. Why: Syntax. Location: file.
16. run-constants.yaml: Add parent_slide_count: null. Why: Override. Location: file.
17. run-constants.yaml: Add target_total_runtime: null. Why: Override. Location: file.
18. run-constants.yaml: Remove locked_slide_count. Why: Deprecated. Location: file.
19. run-constants.yaml: Remove slide_runtime_average_seconds. Why: Deprecated. Location: file.
20. run-constants.yaml: Remove slide_runtime_variability_scale. Why: Deprecated. Location: file.
21. run-constants.yaml: Add comment "# Deprecated fields removed". Why: Migration. Location: file.
22. run-constants.yaml: Validate YAML. Why: Syntax. Location: file.
23. state/config/schemas/run-constants.schema.yaml: Add parent_slide_count field. Why: Validation. Location: schema.
24. state/config/schemas/run-constants.schema.yaml: Add target_total_runtime field. Why: Validation. Location: schema.
25. state/config/schemas/run-constants.schema.yaml: Remove locked_slide_count. Why: Deprecated. Location: schema.
26. state/config/schemas/run-constants.schema.yaml: Remove slide_runtime_average_seconds. Why: Deprecated. Location: schema.
27. state/config/schemas/run-constants.schema.yaml: Remove slide_runtime_variability_scale. Why: Deprecated. Location: schema.
28. state/config/schemas/run-constants.schema.yaml: Update version to 1.2. Why: Version. Location: schema.
29. state/config/schemas/run-constants.schema.yaml: Test schema validation. Why: Test. Location: schema.
30. state/config/schemas/run-constants.schema.yaml: Add description for new fields. Why: Doc. Location: schema.

## Phase 2: Script Rewrites (31-80)
31. scripts/utilities/slide_count_runtime_estimator.py: Rename function estimate_slide_count to estimate_parent_slide_count_and_runtime. Why: New abstraction. Location: def.
32. scripts/utilities/slide_count_runtime_estimator.py: Add import yaml. Why: Profile loading. Location: imports.
33. scripts/utilities/slide_count_runtime_estimator.py: Add function load_experience_profile. Why: Profile loader. Location: new function.
34. scripts/utilities/slide_count_runtime_estimator.py: In load_experience_profile, read state/config/experience-profiles.yaml. Why: Canonical. Location: function body.
35. scripts/utilities/slide_count_runtime_estimator.py: Add error handling for missing profile. Why: Robustness. Location: function.
36. scripts/utilities/slide_count_runtime_estimator.py: Update main function to accept experience_profile param. Why: Profile-aware. Location: def main.
37. scripts/utilities/slide_count_runtime_estimator.py: Load profile in main. Why: Use data. Location: main body.
38. scripts/utilities/slide_count_runtime_estimator.py: Replace locked_slide_count with parent_slide_count. Why: Rename. Location: all occurrences.
39. scripts/utilities/slide_count_runtime_estimator.py: Calculate total_slide_estimate = parent_slide_count * avg_interstitials_per_cluster. Why: Expansion. Location: estimation logic.
40. scripts/utilities/slide_count_runtime_estimator.py: Add cluster_expansion lookup from profile. Why: Profile-driven. Location: estimation.
41. scripts/utilities/slide_count_runtime_estimator.py: Calculate target_total_runtime from parent_slide_count * avg_slide_runtime. Why: Time estimate. Location: estimation.
42. scripts/utilities/slide_count_runtime_estimator.py: Add variability scaling using runtime_variability_scale from profile. Why: Realistic. Location: estimation.
43. scripts/utilities/slide_count_runtime_estimator.py: Remove slide_runtime_average_seconds param. Why: Deprecated. Location: function sig.
44. scripts/utilities/slide_count_runtime_estimator.py: Remove slide_runtime_variability_scale param. Why: Deprecated. Location: function sig.
45. scripts/utilities/slide_count_runtime_estimator.py: Add CLI arg --experience-profile. Why: Input. Location: argparse.
46. scripts/utilities/slide_count_runtime_estimator.py: Add CLI arg --parent-slide-count. Why: Input. Location: argparse.
47. scripts/utilities/slide_count_runtime_estimator.py: Add CLI arg --target-runtime. Why: Input. Location: argparse.
48. scripts/utilities/slide_count_runtime_estimator.py: Update usage docstring. Why: Doc. Location: top.
49. scripts/utilities/slide_count_runtime_estimator.py: Add unit test for new function. Why: Coverage. Location: test_*.py.
50. scripts/utilities/slide_count_runtime_estimator.py: Add integration test for profile loading. Why: Coverage. Location: test_*.py.
51. scripts/utilities/operator_polling.py: Update poll for parent_slide_count instead of locked_slide_count. Why: Rename. Location: poll logic.
52. scripts/utilities/operator_polling.py: Add poll for target_total_runtime. Why: New control. Location: poll logic.
53. scripts/utilities/operator_polling.py: Remove poll for slide_runtime_average_seconds. Why: Deprecated. Location: poll logic.
54. scripts/utilities/operator_polling.py: Remove poll for slide_runtime_variability_scale. Why: Deprecated. Location: poll logic.
55. scripts/utilities/operator_polling.py: Add validation for parent_slide_count range. Why: Bounds. Location: validation.
56. scripts/utilities/operator_polling.py: Add validation for target_total_runtime. Why: Sanity. Location: validation.
57. scripts/utilities/operator_polling.py: Update UI text for new fields. Why: UX. Location: UI strings.
58. scripts/utilities/operator_polling.py: Add help text for parent_slide_count. Why: Doc. Location: help.
59. scripts/utilities/operator_polling.py: Add help text for target_total_runtime. Why: Doc. Location: help.
60. scripts/utilities/operator_polling.py: Update test fixtures. Why: Coverage. Location: test fixtures.
61. scripts/utilities/operator_polling.py: Add test for new validations. Why: Coverage. Location: tests.
62. scripts/utilities/operator_polling.py: Update integration test. Why: Coverage. Location: tests.
63. scripts/utilities/operator_polling.py: Add logging for new fields. Why: Debug. Location: logging.
64. scripts/utilities/operator_polling.py: Update error messages. Why: UX. Location: error handling.
65. scripts/utilities/operator_polling.py: Add comment for new logic. Why: Doc. Location: code.
66. scripts/utilities/operator_polling.py: Refactor poll function for modularity. Why: Clean code. Location: function.
67. scripts/utilities/operator_polling.py: Add type hints for new params. Why: Type safety. Location: function sig.
68. scripts/utilities/operator_polling.py: Update docstring. Why: Doc. Location: function.
69. scripts/utilities/operator_polling.py: Add example usage. Why: Doc. Location: docstring.
70. scripts/utilities/operator_polling.py: Test edge cases. Why: Robustness. Location: tests.
71. scripts/utilities/operator_polling.py: Add performance test. Why: Performance. Location: tests.
72. scripts/utilities/operator_polling.py: Update changelog. Why: History. Location: changelog.
73. scripts/utilities/operator_polling.py: Add migration note. Why: Migration. Location: code.
74. scripts/utilities/operator_polling.py: Validate input types. Why: Type safety. Location: validation.
75. scripts/utilities/operator_polling.py: Add default values. Why: UX. Location: defaults.
76. scripts/utilities/operator_polling.py: Update version. Why: Version. Location: version.
77. scripts/utilities/operator_polling.py: Add feature flag. Why: Gradual rollout. Location: flag.
78. scripts/utilities/operator_polling.py: Update dependencies. Why: Dependencies. Location: imports.
79. scripts/utilities/operator_polling.py: Add monitoring. Why: Observability. Location: monitoring.
80. scripts/utilities/operator_polling.py: Final review. Why: Quality. Location: review.

## Phase 3: Prompt Pack Changes (81-120)
81. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.5 poll to ask for parent_slide_count. Why: New abstraction. Location: Prompt 4.5.
82. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Add target_total_runtime to Prompt 4.5. Why: Time control. Location: Prompt 4.5.
83. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Remove locked_slide_count from Prompt 4.5. Why: Deprecated. Location: Prompt 4.5.
84. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Remove slide_runtime_average_seconds from Prompt 4.5. Why: Deprecated. Location: Prompt 4.5.
85. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Remove slide_runtime_variability_scale from Prompt 4.5. Why: Deprecated. Location: Prompt 4.5.
86. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Add explanation for parent_slide_count. Why: Doc. Location: Prompt 4.5.
87. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Add explanation for target_total_runtime. Why: Doc. Location: Prompt 4.5.
88. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update example in Prompt 4.5. Why: Example. Location: Prompt 4.5.
89. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Add validation note for Prompt 4.5. Why: Validation. Location: Prompt 4.5.
90. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.6 to use new fields. Why: Consistency. Location: Prompt 4.6.
91. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.7 to use new fields. Why: Consistency. Location: Prompt 4.7.
92. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.8 to use new fields. Why: Consistency. Location: Prompt 4.8.
93. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.9 to use new fields. Why: Consistency. Location: Prompt 4.9.
94. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.10 to use new fields. Why: Consistency. Location: Prompt 4.10.
95. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.11 to use new fields. Why: Consistency. Location: Prompt 4.11.
96. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.12 to use new fields. Why: Consistency. Location: Prompt 4.12.
97. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.13 to use new fields. Why: Consistency. Location: Prompt 4.13.
98. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.14 to use new fields. Why: Consistency. Location: Prompt 4.14.
99. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.15 to use new fields. Why: Consistency. Location: Prompt 4.15.
100. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.16 to use new fields. Why: Consistency. Location: Prompt 4.16.
101. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.17 to use new fields. Why: Consistency. Location: Prompt 4.17.
102. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.18 to use new fields. Why: Consistency. Location: Prompt 4.18.
103. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.19 to use new fields. Why: Consistency. Location: Prompt 4.19.
104. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.20 to use new fields. Why: Consistency. Location: Prompt 4.20.
105. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.21 to use new fields. Why: Consistency. Location: Prompt 4.21.
106. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.22 to use new fields. Why: Consistency. Location: Prompt 4.22.
107. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.23 to use new fields. Why: Consistency. Location: Prompt 4.23.
108. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.24 to use new fields. Why: Consistency. Location: Prompt 4.24.
109. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.25 to use new fields. Why: Consistency. Location: Prompt 4.25.
110. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.26 to use new fields. Why: Consistency. Location: Prompt 4.26.
111. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.27 to use new fields. Why: Consistency. Location: Prompt 4.27.
112. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.28 to use new fields. Why: Consistency. Location: Prompt 4.28.
113. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.29 to use new fields. Why: Consistency. Location: Prompt 4.29.
114. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.30 to use new fields. Why: Consistency. Location: Prompt 4.30.
115. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.31 to use new fields. Why: Consistency. Location: Prompt 4.31.
116. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.32 to use new fields. Why: Consistency. Location: Prompt 4.32.
117. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.33 to use new fields. Why: Consistency. Location: Prompt 4.33.
118. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.34 to use new fields. Why: Consistency. Location: Prompt 4.34.
119. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.35 to use new fields. Why: Consistency. Location: Prompt 4.35.
120. docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md: Update Prompt 4.36 to use new fields. Why: Consistency. Location: Prompt 4.36.

## Phase 4: Test Updates (121-170)
121. tests/test_slide_count_runtime_estimator.py: Update test for new function name. Why: Rename. Location: test function.
122. tests/test_slide_count_runtime_estimator.py: Add test for profile loading. Why: New feature. Location: new test.
123. tests/test_slide_count_runtime_estimator.py: Update test fixtures for new params. Why: Params. Location: fixtures.
124. tests/test_slide_count_runtime_estimator.py: Remove tests for deprecated params. Why: Deprecated. Location: tests.
125. tests/test_slide_count_runtime_estimator.py: Add test for expansion calculation. Why: New logic. Location: new test.
126. tests/test_slide_count_runtime_estimator.py: Add test for time estimate. Why: New logic. Location: new test.
127. tests/test_slide_count_runtime_estimator.py: Update integration test. Why: Integration. Location: test.
128. tests/test_slide_count_runtime_estimator.py: Add performance test. Why: Performance. Location: test.
129. tests/test_slide_count_runtime_estimator.py: Update docstring. Why: Doc. Location: test.
130. tests/test_slide_count_runtime_estimator.py: Add edge case test. Why: Edge. Location: test.
131. tests/test_operator_polling.py: Update test for new poll fields. Why: New fields. Location: test.
132. tests/test_operator_polling.py: Add test for validation. Why: Validation. Location: test.
133. tests/test_operator_polling.py: Update fixtures. Why: Fixtures. Location: fixtures.
134. tests/test_operator_polling.py: Remove deprecated tests. Why: Deprecated. Location: tests.
135. tests/test_operator_polling.py: Add UI test. Why: UI. Location: test.
136. tests/test_operator_polling.py: Add error handling test. Why: Error. Location: test.
137. tests/test_operator_polling.py: Update integration test. Why: Integration. Location: test.
138. tests/test_operator_polling.py: Add logging test. Why: Logging. Location: test.
139. tests/test_operator_polling.py: Update docstring. Why: Doc. Location: test.
140. tests/test_operator_polling.py: Add type hint test. Why: Type. Location: test.
141. tests/test_generate_storyboard.py: Update test for new runtime fields. Why: Fields. Location: test.
142. tests/test_generate_storyboard.py: Add test for variability. Why: Variability. Location: test.
143. tests/test_generate_storyboard.py: Update fixtures. Why: Fixtures. Location: fixtures.
144. tests/test_generate_storyboard.py: Remove deprecated tests. Why: Deprecated. Location: tests.
145. tests/test_generate_storyboard.py: Add edge case test. Why: Edge. Location: test.
146. tests/test_generate_storyboard.py: Update integration test. Why: Integration. Location: test.
147. tests/test_generate_storyboard.py: Add performance test. Why: Performance. Location: test.
148. tests/test_generate_storyboard.py: Update docstring. Why: Doc. Location: test.
149. tests/test_generate_storyboard.py: Add logging test. Why: Logging. Location: test.
150. tests/test_generate_storyboard.py: Add type hint test. Why: Type. Location: test.
151. tests/test_prepare_irene_pass2_handoff.py: Update test for new envelope fields. Why: Fields. Location: test.
152. tests/test_prepare_irene_pass2_handoff.py: Add test for packing. Why: Packing. Location: test.
153. tests/test_prepare_irene_pass2_handoff.py: Update fixtures. Why: Fixtures. Location: fixtures.
154. tests/test_prepare_irene_pass2_handoff.py: Remove deprecated tests. Why: Deprecated. Location: tests.
155. tests/test_prepare_irene_pass2_handoff.py: Add edge case test. Why: Edge. Location: test.
156. tests/test_prepare_irene_pass2_handoff.py: Update integration test. Why: Integration. Location: test.
157. tests/test_prepare_irene_pass2_handoff.py: Add performance test. Why: Performance. Location: test.
158. tests/test_prepare_irene_pass2_handoff.py: Update docstring. Why: Doc. Location: test.
159. tests/test_prepare_irene_pass2_handoff.py: Add logging test. Why: Logging. Location: test.
160. tests/test_prepare_irene_pass2_handoff.py: Add type hint test. Why: Type. Location: test.
161. tests/test_cluster_density_controls.md: Update references to new fields. Why: References. Location: doc.
162. tests/test_cluster_density_controls.md: Add new field examples. Why: Examples. Location: doc.
163. tests/test_cluster_density_controls.md: Update schema. Why: Schema. Location: doc.
164. tests/test_cluster_density_controls.md: Add validation. Why: Validation. Location: doc.
165. tests/test_cluster_density_controls.md: Update examples. Why: Examples. Location: doc.
166. tests/test_cluster_density_controls.md: Add comments. Why: Doc. Location: doc.
167. tests/test_cluster_density_controls.md: Update version. Why: Version. Location: doc.
168. tests/test_cluster_density_controls.md: Add changelog. Why: History. Location: doc.
169. tests/test_cluster_density_controls.md: Add migration. Why: Migration. Location: doc.
170. tests/test_cluster_density_controls.md: Final review. Why: Quality. Location: doc.

## Phase 5: Doc Updates (171-220)
171. docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md: Update for consistency. Why: Consistency. Location: similar prompts.
172. docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md: Add new fields. Why: New. Location: prompts.
173. docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md: Remove deprecated. Why: Deprecated. Location: prompts.
174. docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md: Update examples. Why: Examples. Location: prompts.
175. docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md: Add explanations. Why: Doc. Location: prompts.
176. docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md: Update validation. Why: Validation. Location: prompts.
177. docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md: Update version. Why: Version. Location: doc.
178. docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md: Add changelog. Why: History. Location: doc.
179. docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md: Add migration. Why: Migration. Location: doc.
180. docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md: Final review. Why: Quality. Location: doc.
181. docs/parameter-directory.md: Add new parameters. Why: Parameters. Location: directory.
182. docs/parameter-directory.md: Update descriptions. Why: Descriptions. Location: directory.
183. docs/parameter-directory.md: Add examples. Why: Examples. Location: directory.
184. docs/parameter-directory.md: Update schema. Why: Schema. Location: directory.
185. docs/parameter-directory.md: Add validation. Why: Validation. Location: directory.
186. docs/parameter-directory.md: Update references. Why: References. Location: directory.
187. docs/parameter-directory.md: Add comments. Why: Doc. Location: directory.
188. docs/parameter-directory.md: Update version. Why: Version. Location: directory.
189. docs/parameter-directory.md: Add changelog. Why: History. Location: directory.
190. docs/parameter-directory.md: Add migration. Why: Migration. Location: directory.
191. docs/parameter-directory.md: Final review. Why: Quality. Location: directory.
192. docs/governance-dimensions-taxonomy.md: Update for new controls. Why: Controls. Location: taxonomy.
193. docs/governance-dimensions-taxonomy.md: Add new dimensions. Why: Dimensions. Location: taxonomy.
194. docs/governance-dimensions-taxonomy.md: Update examples. Why: Examples. Location: taxonomy.
195. docs/governance-dimensions-taxonomy.md: Add validation. Why: Validation. Location: taxonomy.
196. docs/governance-dimensions-taxonomy.md: Update references. Why: References. Location: taxonomy.
197. docs/governance-dimensions-taxonomy.md: Add comments. Why: Doc. Location: taxonomy.
198. docs/governance-dimensions-taxonomy.md: Update version. Why: Version. Location: taxonomy.
199. docs/governance-dimensions-taxonomy.md: Add changelog. Why: History. Location: taxonomy.
200. docs/governance-dimensions-taxonomy.md: Add migration. Why: Migration. Location: taxonomy.
201. docs/governance-dimensions-taxonomy.md: Final review. Why: Quality. Location: taxonomy.
202. docs/lane-matrix.md: Update for new lanes. Why: Lanes. Location: matrix.
203. docs/lane-matrix.md: Add new lanes. Why: Lanes. Location: matrix.
204. docs/lane-matrix.md: Update examples. Why: Examples. Location: matrix.
205. docs/lane-matrix.md: Add validation. Why: Validation. Location: matrix.
206. docs/lane-matrix.md: Update references. Why: References. Location: matrix.
207. docs/lane-matrix.md: Add comments. Why: Doc. Location: matrix.
208. docs/lane-matrix.md: Update version. Why: Version. Location: matrix.
209. docs/lane-matrix.md: Add changelog. Why: History. Location: matrix.
210. docs/lane-matrix.md: Add migration. Why: Migration. Location: matrix.
211. docs/lane-matrix.md: Final review. Why: Quality. Location: matrix.
212. docs/operations-context.md: Update for new operations. Why: Operations. Location: context.
213. docs/operations-context.md: Add new operations. Why: Operations. Location: context.
214. docs/operations-context.md: Update examples. Why: Examples. Location: context.
215. docs/operations-context.md: Add validation. Why: Validation. Location: context.
216. docs/operations-context.md: Update references. Why: References. Location: context.
217. docs/operations-context.md: Add comments. Why: Doc. Location: context.
218. docs/operations-context.md: Update version. Why: Version. Location: context.
219. docs/operations-context.md: Add changelog. Why: History. Location: context.
220. docs/operations-context.md: Add migration. Why: Migration. Location: context.
221. docs/operations-context.md: Final review. Why: Quality. Location: context.

## Phase 6: Validation and Regression (222-250)
222. Run pytest on all updated tests. Why: Regression. Location: command line.
223. Run yamllint on config files. Why: Syntax. Location: command line.
224. Run mypy on scripts. Why: Type. Location: command line.
225. Run flake8 on scripts. Why: Style. Location: command line.
226. Run coverage on tests. Why: Coverage. Location: command line.
227. Run integration tests. Why: Integration. Location: command line.
228. Run performance tests. Why: Performance. Location: command line.
229. Run security scan. Why: Security. Location: command line.
230. Run accessibility test. Why: Accessibility. Location: command line.
231. Run load test. Why: Load. Location: command line.
232. Run stress test. Why: Stress. Location: command line.
233. Run usability test. Why: Usability. Location: command line.
234. Run compatibility test. Why: Compatibility. Location: command line.
235. Run documentation test. Why: Doc. Location: command line.
236. Run code review. Why: Review. Location: manual.
237. Run peer review. Why: Review. Location: manual.
238. Run QA review. Why: Review. Location: manual.
239. Run security review. Why: Review. Location: manual.
240. Run performance review. Why: Review. Location: manual.
241. Run usability review. Why: Review. Location: manual.
242. Run compatibility review. Why: Review. Location: manual.
243. Run documentation review. Why: Review. Location: manual.
244. Run final integration test. Why: Integration. Location: command line.
245. Run final regression test. Why: Regression. Location: command line.
246. Run final validation test. Why: Validation. Location: command line.
247. Run final acceptance test. Why: Acceptance. Location: command line.
248. Run final deployment test. Why: Deployment. Location: command line.
249. Run final monitoring test. Why: Monitoring. Location: command line.
250. Run final signoff. Why: Signoff. Location: manual.