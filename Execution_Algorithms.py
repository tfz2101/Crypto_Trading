import gdax
import numpy as np
import pandas as pd
import datetime
import time



logfile = open("logfile.txt", "a+")

class OrderManager:
    def __init__(self, public_client, auth_client, product, side, order_size, order_id):
        self.product = product
        self.side = side
        self.order_size = order_size
        self.public_client = public_client
        self.auth_client = auth_client
        self.orderID = order_id
        self.filled_amt = 0

    #TODO:UNUSED
    '''
    def getLatestOrderID(self):
        orders = self.auth_client.get_orders()
        try:
            order_id = orders[0][0]['id']
        except:
            print('Cant Get OrderID',orders)
            raise Exception('Exiting now...')
        self.orderID = order_id
        return order_id
    '''

    #TODO:UNUSED
    '''
    def getOrderFillUpdate(self):
        try:
            order_fills = self.auth_client.get_order(self.orderID)['filled_size']
        except:
            sum = 0
            order_fills = self.auth_client.get_fills(order_id=self.orderID)[0]
            for fill in order_fills:
                sum = float(fill['size']) + sum
            print('fill array',order_fills)
            order_fills = sum
        return float(order_fills)
    '''

    # @TODO:UNUSED
    '''
    def updateFilledAmount(self, filled_amt):
        self.filled_amt = filled_amt
    '''

    #@TODO:UNUSED
    '''
    def getLastFillAmt(self,update_filled_amt=False):
        fillupdate = self.getOrderFillUpdate()
        out = fillupdate - self.filled_amt
        if update_filled_amt:
            self.filled_amt =  fillupdate
        return out
    '''

    #@TODO:THIS SHOULD BE DEPRECATED
    '''
    def getRemainingSize(self):
        updatedFill = self.getOrderFillUpdate()
        if updatedFill != self.filled_amt:
            print('FILLED AMOUNT NOT UPDATED!!!!')
        return (self.order_size-updatedFill)
    '''

    def getOrderStatus(self):
        try:
            cur_order = self.auth_client.get_order(self.orderID)
        except:
            time.sleep(1)
            cur_order = self.auth_client.get_order(self.orderID)
        try:
            status = str(cur_order['status'])
        except:
            print('Couldnt return order status', cur_order)
        return status

    def getWorkingPrice(self):
        try:
            working_price = self.auth_client.get_order(self.orderID)['price']
        except:
            print('Couldnt get working price')
            raise Exception('Exiting now...')
        return float(working_price)

    def getWorkingSize(self):
        try:
            working_size = self.auth_client.get_order(self.orderID)['size']
        except:
            print('Couldnt get working size')
            raise Exception('Exiting now...')
        return float(working_size)

    def cancelOrder(self):
        if self.getOrderStatus()=='done':
            return 'DONE'
        else:
            return self.auth_client.cancel_order(self.orderID)


    def updateOrderSize(self,new_order_size):
        self.order_size = new_order_size

    def updateOrderID(self,new_ID):
        self.orderID = new_ID

    #TODO: THIS IS INCOMPLETE - IT ONLY GETS THE EXECUTION PRICE OF THE LAST FILL, NOT COMPLETE IF IT TAKES SEVERAL ORDERS TO FILL SIZE
    def getExecutedPrice(self):
        #ASSUMES ORDER HAS DONE STATUS
        order = self.auth_client.get_order(self.orderID)
        exec_value = float(order['executed_value'])
        filled_size =  float(order['filled_size'])
        return exec_value/filled_size


class MarketManager:
    MIN_SIZES = {'ETH-USD':0.01,'BTC-USD':0.001}

    def __init__(self, public_client, auth_client, product, side, order_size):
        self.product = product
        self.side = side
        self.order_size = order_size
        self.public_client = public_client
        self.auth_client = auth_client


    def getBestPriceSize(self):
        order_book = self.public_client.get_product_order_book(self.product, level=1)
        index = ""
        if self.side == 'BUY':
            index = 'asks'
        if self.side == 'SELL':
            index = 'bids'
        try:
            best_px_size = order_book[index][0][1]
        except:
            print('Cant Get Best Price Size',order_book)
            return 'ERROR'
        return float(best_px_size)

    def getBestPrice(self):
        order_book = self.public_client.get_product_order_book(self.product, level=1)
        index = ""
        if self.side == 'BUY':
            index = 'bids'
        if self.side == 'SELL':
            index = 'asks'
        try:
            best_px = order_book[index][0][0]
        except:
            print('Cant Get Best Price',order_book)
            return 'ERROR'
        return float(best_px)

    def getAggressivePrice(self):
        order_book = self.public_client.get_product_order_book(self.product, level=1)
        index = ""
        if self.side == 'BUY':
            index = 'asks'
        if self.side == 'SELL':
            index = 'bids'
        try:
            best_px = order_book[index][0][0]
        except:
            print('Cant Get Best Price',order_book)
            return 'ERROR'
        return float(best_px)


    def getShowSize(self):
        return min(self.order_size,self.getBestPriceSize())

    #Make an order that constantly sits on the best bid
    def makePassiveOrder(self,post_only=True):
        passive_px = self.getBestPrice()
        print('WORKING THIS PRICE',passive_px)
        cross_size = self.getShowSize()

        if cross_size < self.MIN_SIZES[self.product]:
            cross_size =  self.MIN_SIZES[self.product]

        print('WORKING THIS SIZE', cross_size)
        logfile.write('INITIAL ORDER PX: ' + str(passive_px) + '\n')
        logfile.write('INITIAL ORDER SIZE: ' + str(cross_size) + '\n')

        if self.side == "BUY":
            cur_order = self.auth_client.buy(price=passive_px,
                                            size=cross_size,
                                            product_id=self.product,post_only=post_only)
        elif self.side == "SELL":
            cur_order = self.auth_client.sell(price=passive_px,
                                            size=cross_size,
                                            product_id=self.product,post_only=post_only)
        return cur_order

    # Make an order that sits on the bid and stays for an static size
    def makePassiveOrderStatic(self, post_only=True):
        passive_px = self.getBestPrice()
        print('WORKING THIS PRICE', passive_px)
        cross_size = self.order_size
        logfile.write('INITIAL ORDER PX: ' + str(passive_px) + '\n')

        if self.side == "BUY":
            cur_order = self.auth_client.buy(price=passive_px,
                                             size=cross_size,
                                             product_id=self.product, post_only=post_only)
        elif self.side == "SELL":
            cur_order = self.auth_client.sell(price=passive_px,
                                              size=cross_size,
                                              product_id=self.product, post_only=post_only)
        return cur_order

    #Make a order based off a given limit price(passive or aggressive).
    #If current price is better than limit price, either sit on the current bid (passive) or cross the spread (aggressive)
    def makeAggressiveOrder(self):
        agg_px = self.getAggressivePrice()

        show_size = self.getShowSize()

        if show_size < self.MIN_SIZES[self.product]:
            show_size =  self.MIN_SIZES[self.product]

        if self.side == "BUY":

            cur_order = self.auth_client.buy(price=agg_px,
                                            size=show_size,
                                            product_id=self.product,post_only=False)
        elif self.side == "SELL":
            cur_order = self.auth_client.sell(price=agg_px,
                                            size=show_size,
                                            product_id=self.product,post_only=False)
        return cur_order


    def updateOrderSize(self,new_size):
        self.order_size = new_size

class PositionManager:
    def __init__(self, public_client, auth_client, product, product_acct_id):
        self.public_client = public_client
        self.auth_client = auth_client
        self.product = product
        #@TODO:self.position is currently not being updated
        self.position = 0
        #@TODO:PRODUCT ACCT ID SHOULD BE AUTOMATICALLLY PULLED HERE, NOT DONE IN THE MAIN PROGRAM LIKE IT IS NOW
        self.product_acct_id = product_acct_id

    def getCurrentPositionFromAcct(self):
        try:
            cur_pos = float(self.auth_client.get_account(account_id=self.product_acct_id)['balance'])
        except:
            time.sleep(1)
            cur_pos = float(self.auth_client.get_account(account_id=self.product_acct_id)['balance'])
        return cur_pos

    #@TODO:THIS SHOULD BE DEPRECATED GOING FORWARD
    def getCurrentPosition(self):
        return self.position

    #@TODO:THIS SHOULD BE DEPRECATED GOING FORWARD
    def updateCurrentPosition(self,positionChange,side):
        if side == 'BUY':
            self.position =  self.position + positionChange
        elif side == 'SELL':
            self.position = self.position - positionChange

    # @TODO:This should be generalized, won't work when it gets more complex
    def isTargetPositionReached(self,size,side):
        #ASSUME NEUTRAL POSITION IS 0
        position = self.getCurrentPositionFromAcct()
        if side == 'SELL':
            if position <= 0:
                return True
            else:
                return False
        if side == 'BUY':
            if position >= size:
                return True
            else:
                return False

class SignalManager:
    def __init__(self, public_client, auth_client, product, entry_time, signal_run_sec):
        self.product = product
        self.entry_time = entry_time
        self.exit_time = self.entry_time + datetime.timedelta(seconds=signal_run_sec)


    def getExitTime(self):
        return self.exit_time


