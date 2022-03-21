from brownie import accounts,network, interface, config, exceptions
from web3 import Web3

# List of all the testing environments.
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development","mainnet-fork"]

# To interact with any contract over the world you need an
# - ABI
# - Contract Address
# You can actually generate ABI from Interface. (Just make sure that Interface has the functions you need to interact with.)


def deposit_weth(value=None):
    """Deposits your ETH & Converts them to ERC20 Tradeable WETH.
    
    Arguements: 
        value(default=0.1): The amount of ETH you want to convert to WETH."""

    # Getting the account
    account = get_account()

    # Setting up our Weth Interface.
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])

    # Check's if the amount(amt) isn't None or 0
    if value != None and value != 0:
        # There is a value to be transferred from ETH to WETH. Hence Transact.
        tx = weth.deposit({"from":account, "value": value * 10 ** 18})
        tx.wait(1)
        print(f'[WETH] Deposited {value} WETH to address {account}')
        return tx
    else:
        # If value isn't given by user or if value is not specified. Raise a Transaction Error
        raise exceptions.TransactionError("[WETH] The transaction could not be processed since amount isn't specified or is 0.") 


def balance():
    """Returns the balance of our WETH contract."""
    
    # Getting Account
    account = get_account()
    
    # Setting Up Weth Interface.
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    
    # Converting the balance from WEI to WETH.
    balance = Web3.fromWei(weth.balanceOf(account),"ether")
    
    # Returns the balance of WETH.
    return balance

def withdraw_weth(amt=None):
    """Withdraws WETH & Converts them to ETH.
    
    Arguements: 
        amt(default=max i.e. withdraws everything): The amount of ETH you want to conver to WETH."""
    
    # Getting Account
    account = get_account()
 
    # Setting Up Weth Interface.
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
   
    # Check's if the amount(amt) isn't None or 0
    if amt != None and amt != 0:
        # There is a value to be transferred from WETH to ETH. Hence Transact.
        tx = weth.withdraw(amt * 10 ** 18,{"from": account})
        tx.wait(1)
        print(f'[WETH] Withdrew {amt} WETH to address {account}')
        return tx
    else:
        # If value isn't given by user or if value is not specified. Raise a Transaction Error
        raise exceptions.TransactionError("[WETH] The transaction could not be processed since amount isn't specified or is 0.") 
       

    
def get_account(index=None, id=None):
    """Returns the account depending upon network."""
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id: 
        return accounts.load(id)
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    return None


def pretty_output(action=""):
    # Used to seprate the output
    s=""
    r = range(0,100)
    for i in r:
        if i == (len(r)/2):
            s+=action
        s+='='
    print(s)

