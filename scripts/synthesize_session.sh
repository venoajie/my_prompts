Suggested Enhancements
For very complex targets like this, a common best practice is to move the logic into a dedicated shell script.
Create scripts/synthesize_session.sh: Move the entire multi-line command block from the end-session target into this new script file. The script would take the LOG file path as an argument.
Simplify the Makefile: The end-session target in the Makefile would then become a single, clean line:
.PHONY: end-session
end-session:
    @./scripts/synthesize_session.sh $(LOG)