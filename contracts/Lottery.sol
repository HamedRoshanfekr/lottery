// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase, Ownable {

    address payable[] public players;
    address payable public recentWinner;
    uint256 public randomness;
    uint256 public usdEntryFee;
    uint256 public fee;
    bytes32 keyhash;
    AggregatorV3Interface public priceFeed;
    enum LOTTERY_STATES {
        OPEN, // 0
        CLOSED, // 1
        CALCULATING_WINNER // 2
    }

    LOTTERY_STATES public lotteryState;
    event RequestedRandomness(bytes32 requestId);

    constructor (address _priceFeed, address _vrfCoordinator, address _link, uint256 _fee, bytes32 _keyhash) public
     VRFConsumerBase(_vrfCoordinator, _link) {
        usdEntryFee = 50 * (10 ** 18);
        priceFeed = AggregatorV3Interface(_priceFeed);
        lotteryState = LOTTERY_STATES.CLOSED;
        fee = _fee;
        keyhash = _keyhash;
    }

    function enter() public payable {
        require(lotteryState == LOTTERY_STATES.OPEN);
        require(msg.value >= getEntranceFee(), "Not enough ether!");
        players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        (,int256 price,,,) = priceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * (10 ** 10);
        uint256 costToEnter = (usdEntryFee * 10 ** 18) / adjustedPrice;
        return costToEnter;
    }

    function startLottery() public onlyOwner {
        require(lotteryState == LOTTERY_STATES.CLOSED);
        lotteryState = LOTTERY_STATES.OPEN;
    }

    function endLottery() public onlyOwner {
//        uint256(
//            keccak256(
//                abi.encodePacked(
//                    block.number,
//                    msg.sender,
//                    block.difficulty,
//                    block.timestamp
//                )
//            )
//        ) % players.length;
        lotteryState = LOTTERY_STATES.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyhash, fee);
        emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness) internal override {
        require(lotteryState == LOTTERY_STATES.CALCULATING_WINNER, "ooh");
        require(_randomness > 0, "hmmm");
        randomness = _randomness;
        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        recentWinner.transfer(address(this).balance);
        players = new address payable[](0);
        lotteryState = LOTTERY_STATES.CLOSED;
    }
}