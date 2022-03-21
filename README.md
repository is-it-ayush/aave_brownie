# AAVE Programatic Interaction

This project is made to interact with AAVE in a programatic way. It does the following:
- Convert's ETH into WETH.
- Deposits WETH into AAVE.
- Borrow's DAI
- Repay's DAI

> WETH is the tradeable ERC20 version of ETH. WETH stands for Wrapped Ether. Since ETH was created before the ERC20 Standard was framed. Hence, came the need to covert ETH for it to be tradeable with ERC20 Tokens.

# Testing
**Integration Testing**: Kovan <br>
**Unit Tests**: mainnet-fork (I should use Devlopment with Mocking but I want to keep it simple for now.)

# Known Issues:
- None Yet! Let me know by submitting one.
- If you face any issues, kindly recheck the latest address on the internet and update them accordingly in ```brownie-config.yaml```.