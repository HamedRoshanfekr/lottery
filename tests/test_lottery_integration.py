import time

from brownie import network, Lottery
from scripts.helper import LOCAL_BLOCKCHAIN_ENVIRONMENT, get_account, fund_with_link
import pytest
from scripts.deploy_lottery import deploy_lottery

def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENT:
        pytest.skip()
    account = get_account()
    lottery = deploy_lottery()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery.address)
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    print(f"req id is {request_id}")
    time.sleep(180)
    print(f"rng is {lottery.randomness()}")
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
