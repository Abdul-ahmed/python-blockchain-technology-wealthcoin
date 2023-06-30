// WealthCoin ICO

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract WealthCoin {

    // Total available WealthCoin
    uint public max_wealthcoin = 1000000;

    // WealthCoin to USD
    uint public wealthcoin_to_usd = 100;

    // Total wealthcoin bought by the investors
    uint public total_wealthcoin_bought = 0;

    // Investors Equity
    mapping (address => uint) equity_in_wealthcoin;
    mapping (address => uint) equity_in_usd;

    modifier can_buy_wealthcoin(uint investment_amount_in_usd) {
        require(investment_amount_in_usd * wealthcoin_to_usd + total_wealthcoin_bought <= max_wealthcoin);
        _;
    }

    function wealthcoin_coin_equity(address investor_address) external view returns (uint) {
        return equity_in_wealthcoin[investor_address];
    }

    function wealthcoin_usd_equity(address investor_address) external view returns (uint) {
        return equity_in_usd[investor_address];
    }

    // Buy WealthCoin
    function buy_wealthcoin(address investor_address, uint investment_amount_in_usd) external can_buy_wealthcoin(investment_amount_in_usd) {
        uint wealthcoin_bought = investment_amount_in_usd * wealthcoin_to_usd;

        equity_in_wealthcoin[investor_address] += wealthcoin_bought;
        equity_in_usd[investor_address] = equity_in_wealthcoin[investor_address]/wealthcoin_to_usd;

        total_wealthcoin_bought += wealthcoin_bought;
    }

    // Sell WealthCoin
    function sell_wealthcoin(address investor_address, uint wealthcoin_amount_selling) external {
        equity_in_wealthcoin[investor_address] -= wealthcoin_amount_selling;
        equity_in_usd[investor_address] = equity_in_wealthcoin[investor_address]/wealthcoin_to_usd;
        total_wealthcoin_bought -= wealthcoin_amount_selling;
    }
}

