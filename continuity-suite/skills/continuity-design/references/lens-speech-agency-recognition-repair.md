# Speech agency, recognition, and repair

## Generalized principles

- Treat speech as one accessible modality, not the definition of access: support the full task through appropriate speech, text, keyboard, switch, touch, visual, auditory or assisted combinations; let users change modality at any turn without losing context; avoid interference between simultaneous inputs; and validate the entire outcome, not merely microphone activation, across sensory, motor, speech, language and cognitive needs.
- Preserve the distinction between signal, words, meaning, intent, authorization and outcome: expose what the system captured and inferred at the useful grain; represent uncertainty without claiming that a score proves correctness; ground ordinary parameters lightly; explicitly confirm consequential parameters and actions; and never let recognition alone authorize irreversible, financial, legal, health, safety or physical-world effects.
- Design repair as a first-class cooperative path: expect hesitation, self-correction, code-switching, noise, interruption, no input, no match and system failure; preserve valid context; support one-step spoken or nonspoken correction, repeat, undo and review; explain the specific recoverable problem without blaming speech; bound reprompts; and offer an equivalent route or graceful exit before frustration becomes exclusion.
- Evaluate recognition across the people and conditions that shape real accuracy: measure by language, dialect, accent, age, gender, disability, speech difference, vocabulary, device, microphone, noise, bandwidth and emotional or physical context; test confidence calibration and downstream task harm, not only average word error; provide human review for high-consequence use; and do not make users conform their identity or speech to compensate for systematic gaps.
- Make listening and data use perceptible, bounded and revocable: request microphone and recognition access at the point of need; state whether processing is on-device or remote and whether raw audio, transcript or voice characteristics are retained; keep a persistent accessible capture indicator and immediate stop; minimize purpose, recipients and duration; separate service delivery from model training or personalization; and provide history, access, export and deletion.
- Protect people beyond the primary speaker: account for bystanders, shared devices, confidential spaces, children and voice-biometric inference; avoid exposing partial speech on public displays; require appropriate consent before recording or repurposing another person's voice; prevent synthetic or stored voice from becoming implicit identity proof; and provide private nonvoice routes when speaking would reveal sensitive intent or create danger.

## Method

- Map the task from acoustic capture through recognition, interpretation, authorization, execution and outcome, naming uncertainty and evidence at each boundary.
- Identify all affected speakers and listeners, supported modalities, languages, speech variations, environments and consequences.
- Design contextual permission, persistent listening state, inspectable intent, correction, confirmation, fallback, data controls and bystander protection.
- Set consequence-sensitive review and human escalation, then test recognition and confidence across affected groups and real conditions.
- Measure task completion, correction burden, false action, privacy control, exclusion and downstream harm, and revise the system rather than training users to accommodate it.

## Ethical safeguards

- Do not require speech from people who cannot, should not or do not wish to speak in the current environment.
- Do not interpret accent, fluency, disability, hesitancy, emotion or background noise as competence, honesty, consent or risk.
- Do not use a recognized utterance as proof of speaker identity, free choice or informed authorization.
- Do not conceal continuous, background or remote microphone processing behind a transient indicator.
- Do not make model training, personalization or voice-characteristic analysis inseparable from the requested speech task.
- Do not publish, send or execute uncertain speech without consequence-appropriate review.
- Do not retain child or bystander voice beyond a clearly justified, consented and bounded purpose.
- Do not report only average accuracy when subgroup or context failures create unequal burden or harm.
- Do not force repeated speech after recognition failure when another modality or human route is available.

## Variation levers

- Increase explicit confirmation, human review and nonvoice verification with consequence, irreversibility, identity reliance and uncertainty.
- Use push-to-talk by default in shared and sensitive settings; justify continuous listening with persistent state, narrow activation and easy interruption.
- Prefer local ephemeral processing where it meets the task; require stronger disclosure and controls as raw audio, transcripts or characteristics travel or persist.
- Adapt timing, vocabulary, examples, language and correction to the individual while preventing personalization from becoming mandatory surveillance.

## Tensions and tradeoffs

- Continuous listening improves fluidity while weakening the clarity of collection boundaries.
- Visible partial recognition supports correction while exposing sensitive speech and increasing cognitive monitoring.
- Personalization can improve atypical-speech accuracy while collecting durable characteristics and interaction history.
- Confirmation reduces harmful misexecution while making routine speech slow and socially awkward.
- A single confidence score simplifies automation while hiding subgroup calibration failures and semantic uncertainty.

## Failure modes

- Voice is the only route through one step of an otherwise multimodal task.
- The system acts on recognized words without separating meaning, intent and authorization.
- A recognition error clears valid context and starts the dialog over.
- People with particular speech patterns must repeat more often but accuracy is reported only in aggregate.
- The microphone indicator disappears even though capture or transmission continues.
- Permission text says improve experience without naming speech processing or retention.
- Training use is bundled with basic voice functionality.
- A nearby person's speech is captured, displayed or retained without notice or control.
- A voice match is treated as sufficient identity or consent.
- After repeated failure, the only guidance is speak clearly or try again.

## Anti-patterns

- Voice-only step.
- Recognition equals authorization.
- Context-destroying repair.
- Average accuracy alibi.
- Invisible capture.
- Vague voice permission.
- Training by default.
- Bystander blind spot.
- Voiceprint means consent.
- Blame-and-repeat loop.

## Acceptance and review questions

- Can every affected user complete the full task through an appropriate modality combination and switch modes without losing context?
- Does the design distinguish captured signal, recognized words, interpreted meaning, user intent, authorization and verified outcome?
- Can errors be repaired cooperatively at the right grain without blame, repeated work or reprompt traps?
- Was recognition and confidence evaluated across relevant language, speech, disability, device, environment and consequence groups using downstream harm measures?
- Are listening state, local or remote processing, raw audio, transcript, characteristics, recipients, retention, training and deletion perceptible and controllable?
- Are bystanders, children, shared devices, confidential environments and voice-identity misuse protected with private nonvoice alternatives?
