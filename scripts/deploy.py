from web3 import Web3
from brownie import config,network, interface,exceptions
from scripts.helpful_scripts import balance, deposit_weth, get_account, pretty_output
from brownie.network.gas.strategies import GasNowStrategy

def deploy():
    # Get Account
    account = get_account()
    # Getting the LendingPool Addresss really Important.
    lending_pool = interface.ILendingPool(get_lending_pool_address())

    # Printing the WETH Balance in our Account
    print(f"[WETH] Balance: {balance()}")
    
    # If WETH Blance get's below 0.1. It deposits ETH into WETHGateway which returns the deposted ETH converted to WETH
    if balance() < 0.2:
        deposit_weth(0.1)
    else:
        print("[WETH] Deposit to WETH Skipped! WETH Balance is greater than 0.2 WETH.")

    # Checking our Collateral. If its below 0.2 ETH. It deposits some WETH into
    if get_stats(lending_pool,account)[2] < 0.2:
        deposit_to_aave(0.1)
    else:
        print("[AAVE] Deposit to AAVE Skipped! Collateral is greater than 0.2 ETH.")
    
    # Returns the User Account Information from AAVE
    get_stats(lending_pool,account,info=True)
    
    # This will borrow 95% of the borrowable eth depeding upon the Collateral Available at either Intrest Rate: 1 = Stable or 2 = Variable
    # borrow(1)

    # Gets the total amount of currently borrowed token.
    total_to_be_paid = get_stats(lending_pool,account)[1]/get_asset_price(config["networks"][network.show_active()]["dai_eth_price_feed"])
    
    # Repay's 99& of borrowed Token.
    repay_all(lending_pool, account,Web3.toWei(total_to_be_paid, "ether"),1)


def borrow(r=1):
    """Borrow's 95% of available DAI.
    
    Arguement:
    r: 1 (Stable), 2 (Variable)

    """
    # Prettifies the output.
    pretty_output("Borrow")
    
    # Get Account
    account = get_account()
    
    # Getting the Lending Pool Address.
    lending_pool = interface.ILendingPool(get_lending_pool_address())
    
    # The total amount of ETH that can be borrowed.
    eth_that_can_be_borrowed = get_stats(lending_pool,account)[0]
    
    # DAI Token Address (Latest as of 21/03/22)
    dai_token = config["networks"][network.show_active()]["dai_token"]
    
    # DAI Asset Price from Chainlink
    dai_eth_price = get_asset_price(config["networks"][network.show_active()]["dai_eth_price_feed"])
 
    # Calculating the total number of DAI tokens that can be borrowed. Basically doing,  (Amount of ETH that can be Borrowed/Price of 1 DAI in ETH) and multiplying it with 0.90 
    amount_to_borrow = (1/dai_eth_price) * (eth_that_can_be_borrowed * 0.95)
    
    # Converting the same to WEI
    amount_to_borrow_in_wei = Web3.toWei(amount_to_borrow,"ether")

    # Executing the Borrowing Code.
    borrow_tx = lending_pool.borrow(dai_token,amount_to_borrow_in_wei, r , 0, account, {"from": account, "priority_fee":"3 gwei"})    
    
    # Waiting 1 Block Confirmation.
    borrow_tx.wait(1)
    
    print(f"[AAVE] Borrowed {amount_to_borrow} DAI.")
    
    # Getting User Account Info from AAVE
    get_stats(lending_pool,account,True)


def repay_all(lending_pool, account, debt, r=1, info=False):
    """Repay's almost 99% of the Borrowed Debt.
    
    Arguement:
        lending_pool: Address of Lending Pool
        account: User Account
        debt: Amount of Debt to be repaid in WEI
        info: To Print Info from get_status() or not.
    """
    pretty_output("Repay")

    # Getting the asset price
    asset = config["networks"][network.show_active()]["dai_token"]
    
    print(Web3.fromWei((debt*0.90),"ether"))
    
    # Approving the ERC20 Token to be transferred.
    approve_erc20(debt,lending_pool.address,asset,account)
    
    # Executing the Repay Transaction. Here debt * 0.99. Only 99% of the debt is paid. 100% cannot be paid sice transaction requires some GAS.
    repay_tx = lending_pool.repay(asset,(debt*0.99),r,account.address,{"from": account, "priority_fee":"3 gwei"})
 
    # Waiting 1 Block Confirmation.
    repay_tx.wait(1)
    print(f'[AAVE] The amount {Web3.fromWei(debt,"ether")} has been repaid.')
    print(f"[AAVE] Your Current Debt: {get_stats(lending_pool,account,info)[1]}")

def get_asset_price(price_feed_address):
    """Returns the asset price from Chainlink of the given PriceFeed Address in ETH.
    
    Arguement:
        price_feed_address: The address of the asset that you want the price of to be returned.
    """
    # Getting the Price of the Asset.
    price = interface.IAggregatorV3(price_feed_address)
    
    # Getting the price in WEI.
    latest_price = price.latestRoundData()[1]
    
    # Converting the price to ETH
    converted_latest_price = Web3.fromWei(latest_price,'ether')

    print(f"[Chainlink] The current price is: {converted_latest_price}")
    return (float(converted_latest_price))

def get_stats(lending_pool,account,info=False):
    """Returns The Avaialable ETH that can be borrowed(0), Total Debt(1), Total Collateral(2) in ETH
    
    Arguement:
        lending_pool: LendingPool Contract
        account: User Account
        info: To Print Info from get_status() or not.
    """
    # Getting the user data as tuple via LendingPool.
    (total_collateral_eth, total_debt_eth, avaiable_borrow_eth, current_liquidation_threshold, ltv, health_factor) = lending_pool.getUserAccountData(account)
    
    # Converting the required data to ETH
    avaiable_borrow_eth = Web3.fromWei(avaiable_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth,"ether")
    total_debt_eth = Web3.fromWei(total_debt_eth,"ether")
    
    # If Info is true. It prints the User Data.
    if info:
        print(f"[AAVE] Total Collateral Deposited ETH: {total_collateral_eth}\n[AAVE] Available ETH that can be Borrowed: {avaiable_borrow_eth}\n[AAVE] Total Debt ETH: {total_debt_eth}\n[AAVE] Health Factor: {health_factor}")
    
    return (float(avaiable_borrow_eth), float(total_debt_eth), float(total_collateral_eth))
 
def deposit_to_aave(amt=None):
    """Deposits the amount to AAVE
    
    Arguemnt:
        amt: The amount of ETH to be deposited into the collateral.
    """
    pretty_output("Deposit")
    
    # Getting the account.
    account = get_account()

    # Gets the ERC20 Token Address.
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    
    # Getting the LedningPool Addresss
    lending_pool = interface.ILendingPool(get_lending_pool_address())

    # Approving the ERC20 Token to be transferred.
    approve_erc20(Web3.toWei(amt,"ether"),lending_pool.address,erc20_address,account)

    # If amount is not None and not 0. Then Execute the Deposit eles throw out an Transaction Error.
    if amt != None and amt != 0:        
        tx = lending_pool.deposit(erc20_address,Web3.toWei(amt,"ether"), account, 0, {"from": account})
        tx.wait(1)
        print(f"[AAVE] Deposited {amt} WETH into AAVE.")
    else:
        raise exceptions.TransactionError("[AAVE] The deposit could process due to missing arguements.") 
 

def approve_erc20(amount, spender, erc20_address, account):
    """Approving the ERC20 Token.
    
    Arugement:
        amount: The amount to be approved in WEI.
        spender: The LendingPool Contract that will be initiating the transfer.
        erc20_address: The address of token which will be transferred.
    """
    # Getting the ERC20 Contract.
    erc20 = interface.IERC20(erc20_address)
    
    # Executing the approve function.
    tx = erc20.approve(spender, amount, {"from": account})
    
    # Waitng for 1 Block Confirmation
    tx.wait(1)
    print(f"[ERC20] Approved ERC20 Token. Status:\t")
    print(f"[ERC20] Address: {spender}\n[ERC20] Amount: {Web3.fromWei(amount,'ether')}\n[ERC20] Token Address: {erc20_address}")
    
    # Returns the Transaction.
    return tx    

def get_lending_pool_address():
    """Returns the current address of the LendingPool via LendingPoolAddressProvider."""
    # Get the provider address. This address is permanently fixed only LendingPool Address Changes.
    provider = interface.ILendingPoolAddressProvider(config["networks"][network.show_active()]["lending_pool_address_provider"])
    
    # Return the address.
    return provider.getLendingPool()

    
def main(): 
    deploy()
