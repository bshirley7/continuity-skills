# Speech input and voice interaction

## Generalized principles

- Introduce speech as a scoped input option with an equivalent route: explain the immediate task, when the microphone opens, whether recognition is local or remote, what is retained and how to stop; request permission in context; never require voice where text, switch, touch, keyboard or assisted input can complete the task; and preserve the user's chosen modality across the full journey.
- Make capture state unambiguous through every transition: distinguish permission requested, ready, listening, paused, processing, low-confidence, complete, cancelled and failed; provide persistent visual and nonvisual feedback, elapsed time and input level without implying accurate recognition; prevent accidental background capture; and keep stop, cancel and modality-switch controls reachable during an utterance.
- Turn recognition into inspectable and editable intent before commitment: show partial and final text where a display exists, preserve language and relevant context, mark uncertain spans without overstating confidence, allow touch, keyboard or speech correction at the word, parameter or whole-request level, retain the original draft until replacement is confirmed, and never make a transcript the sole record when the original audio carries essential meaning.
- Scale confirmation to consequence and reversibility: use lightweight grounding for ordinary search, explicit review for names, addresses, medication, recipients and shared messages, and exact confirmation before payment, consent, deletion, publication or physical control; state what was understood and what will happen; distinguish a recognized utterance from authorized action and a requested action from completed outcome.
- Repair cooperatively across silence, noise, accent, atypical speech and changing intent: do not blame the person; preserve valid parameters; offer context-specific alternatives and examples; support one-step correction, repeat, slower pace, language change and text fallback; bound reprompt loops; and provide a graceful exit or human route rather than repeatedly demanding clearer speech.
- Govern voice as sensitive communication, not disposable interface exhaust: identify whether raw audio, transcript, voice characteristics, contacts or surrounding speech are collected; minimize by task; protect previews on shared devices; separate sending from training or personalization consent; expose history, recipients, retention, download and deletion; and preserve additional protections for children, bystanders and biometric inference.

## Variation levers

- Increase explicit review and block immediate execution with legal, financial, health, safety, identity, publication or physical-world consequence.
- Prefer push-to-talk in shared, sensitive or noisy environments and continuous listening only with unmistakable persistent state and fast interruption.
- Use on-device recognition and short retention where feasible; disclose network processing and additional consent when raw voice or characteristics leave the device.
- Adapt prompts, timing, vocabulary and correction for language, dialect, speech disability, age, noise and task expertise without stereotyping people.

## Tensions and tradeoffs

- Hands-free speed improves access while increasing accidental capture and ambiguous commitment.
- Live partial text supports repair while distracting the user and exposing private speech on nearby screens.
- Personalized recognition may improve accuracy while requiring retention of voice characteristics or history.
- Explicit confirmation prevents costly errors while making ordinary conversation repetitive and cognitively heavy.
- Voice output and input feel natural while encouraging people to overestimate understanding, confidentiality and agency.

## Failure modes

- A microphone icon gives no indication whether the system is listening or processing.
- Permission is requested at launch without explaining the specific speech task or data path.
- Speech immediately sends, purchases, publishes or controls without editable review.
- Recognition confidence is presented as certainty or used to blame the person.
- A correction restarts the entire task and discards valid information.
- Repeated no-match prompts provide no text, touch or human alternative.
- The listening indicator disappears while capture continues in the background.
- Voice history, raw audio or training use cannot be separately inspected or deleted.
- A shared screen displays sensitive partial speech before the user can cancel.
- Voice is marketed as accessible while the rest of the task requires an incompatible input or output mode.

## Anti-patterns

- Ambiguous microphone.
- Permission before purpose.
- Speech equals commitment.
- Confidence equals truth.
- Restart to correct.
- Reprompt trap.
- Invisible listening.
- Voice-data black box.
- Public partial transcript.
- Voice-only accessibility.

## Acceptance and review questions

- Is speech introduced in context with clear collection, processing, retention, stop behavior and a complete equivalent input route?
- Can every user perceive and control permission, ready, listening, paused, processing, uncertainty, completion, cancellation and failure state?
- Can recognized intent be reviewed and corrected at an appropriate grain by speech or another modality before commitment?
- Does confirmation increase with consequence and distinguish recognition, authorization, request and completed outcome?
- Can silence, noise, accent, atypical speech and changed intent be repaired without blame, lost progress or reprompt traps?
- Can people inspect and control raw audio, transcript, personalization, training, recipients, retention and deletion, including protections for children and bystanders?
