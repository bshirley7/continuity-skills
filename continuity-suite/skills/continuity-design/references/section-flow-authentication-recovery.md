# Authentication and account recovery

## Generalized principles

- Separate account identity, sign-in method, verification factor, recovery channel, trusted device, active session, and connected provider as distinct states; show which are configured, verified, current, weaker, unavailable, or incomplete.
- Present the safest suitable method with a plain explanation of what it authenticates, where a credential is stored, which devices can use it, and what fallback remains; stronger security must not silently remove the only recoverable path.
- Design recovery as a visible assurance sequence: identify the account without oversharing, show the masked verification destination, allow alternate or support routes, disclose material side effects, confirm credential change, and state what the person should do next.
- Make security state continuously inspectable through enrolled methods, recovery readiness, device and session context, recent activity, individual revocation, global logout, and explicit completion or risk status.

## Variation levers

- Offer organization sign-on and managed identity prominently in enterprise contexts, while preserving clear account and support routing.
- Scale verification and post-recovery review to account consequence, suspicious activity, device trust, and available recovery evidence.
- Use platform-native passkey and biometric prompts while surrounding them with product-level explanation, completion state, and fallback guidance.

## Tensions and tradeoffs

- More method choice improves reach while increasing uncertainty about which identity or credential applies.
- Masked account clues aid recognition while potentially exposing identity information.
- Stronger recovery checks reduce takeover risk while increasing lockout risk for legitimate users.
- Synchronized passkeys improve convenience while requiring clear device, storage, and fallback understanding.

## Failure modes

- Sign-in methods are presented as interchangeable without explaining account, organization, or credential consequences.
- A stronger factor is enabled before recovery readiness or fallback is established.
- Recovery reports that a message was sent without destination, timing, resend, alternate route, or support.
- A password reset silently changes billing data, sessions, devices, or other account state.
- Security settings show configuration controls but not current enrollment, session, device, or risk state.

## Anti-patterns

- Provider roulette.
- Passkey without provenance.
- MFA before recovery.
- Code sent somewhere.
- Reset with hidden side effects.
- Session list without revocation.
- Security checklist without state.

## Acceptance and review questions

- Can the person tell which account, organization, provider, credential, and factor each route uses?
- Does stronger authentication explain storage, device reach, fallback, recovery readiness, and completion state?
- Does recovery show a masked destination, resend timing, alternate route, support, and material side effects?
- Does the terminal state confirm what changed, which sessions or data were affected, and what happens next?
- Can people inspect and revoke devices, sessions, providers, and factors individually or globally?
- Are account-recognition clues useful without exposing unnecessary identity information?
