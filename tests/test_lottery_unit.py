from scripts.deploy_lottery import deploy_lottery
from scripts.helper import LOCAL_BLOCKCHAIN_ENVIRONMENT, get_account, fund_with_link, get_contract
from web3 import Web3
from brownie import network, exceptions
import pytest
def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act
    entrance_fee = lottery.getEntranceFee()
    # Assert
    expected_entrance_fee = Web3.toWei(0.025, "ether") # 50 / 2000 = 0.025
    assert entrance_fee == expected_entrance_fee

def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act / Assert
    with(pytest.raises(exceptions.VirtualMachineError)):
        lottery.enter({"from": get_account(),"value": lottery.getEntranceFee()})

def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    account = get_account()
    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # Assert
    assert lottery.players(0) == account

def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    account = get_account()
    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery.address)
    lottery.endLottery({"from": account})
    # Assert
    assert lottery.lotteryState() == 2

def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    account = get_account()
    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery.address)
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(request_id, STATIC_RNG, lottery.address,{"from": account})
    # 777 % 3 = 0
    starting_balance_of_account = account.balance()
    lottery_balance = lottery.balance()
    # Assert
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + lottery_balance