from pyteal import *


class Property:
    admin = Addr("../")
    class Variables:
        image = Bytes("IMAGE")
        description = Bytes("DESCRIPTION")
        location = Bytes("LOCATION")
        sellprice = Bytes("SELLPRICE")
        sale = Bytes("SALE")
        likes = Bytes("LIKES")
        owner = Bytes("OWNER")

    class AppMethods:
        like = Bytes("like")
        buy = Bytes("buy")
        sell = Bytes("sell")
        edit = Bytes("edit")

    def application_creation(self):
        return Seq([
            Assert(
                And(
                    Txn.application_args.length() == Int(4),
                    Txn.note() == Bytes("realtor:uv1"),
                    Len(Txn.application_args[0]) > Int(0),
                    Len(Txn.application_args[1]) > Int(0),
                    Len(Txn.application_args[2]) > Int(0),
                    Btoi(Txn.application_args[3]) > Int(0),

                )
            ),

            # Store the transaction arguments into the applications's global's state
            App.globalPut(self.Variables.image, Txn.application_args[0]),
            App.globalPut(self.Variables.description, Txn.application_args[1]),
            App.globalPut(self.Variables.location, Txn.application_args[2]),
            App.globalPut(self.Variables.sellprice,
                          Btoi(Txn.application_args[3])),
            App.globalPut(self.Variables.sale, Int(1)),
            App.globalPut(self.Variables.likes, Int(0)),
            App.globalPut(self.Variables.owner, Txn.sender()),

            Approve(),
        ])

# other users can buy property
    def buy(self):
        valid_number_of_transactions = Global.group_size() == Int(2)

        valid_payment_to_seller = And(
            Gtxn[1].type_enum() == TxnType.Payment,
            Gtxn[1].receiver() == App.globalGet(self.Variables.owner),
            Gtxn[1].amount() == App.globalGet(self.Variables.sellprice),
            Gtxn[1].sender() == Gtxn[0].sender(),
            App.globalGet(self.Variables.sale) == Int(1),

        )

        can_buy = And(valid_number_of_transactions,
                      valid_payment_to_seller)

        update_state = Seq([
            App.globalPut(self.Variables.owner, Txn.sender()),
            App.globalPut(self.Variables.sale, Int(0)),
            Approve()
        ])

        return If(can_buy).Then(update_state).Else(Reject())

    # other users can like property
    def like(self):
        Assert(
            And(
                Global.group_size() == Int(1),
                Txn.sender() != App.globalGet(self.Variables.owner),
                Txn.applications.length() == Int(1),
                Txn.application_args.length() == Int(1),
            ),
            
        ),
        return Seq([
            App.globalPut(self.Variables.likes, App.globalGet(
                self.Variables.likes) + Int(1)),
            Approve()
        ])

   # owner of property can sell property

    def sell(self):
        Assert(
            And(
                Txn.application_args.length() == Int(1),
                Txn.sender() == App.globalGet(self.Variables.owner),
                App.globalGet(self.Variables.sale) == Int(0),
            ),
        ),
        return Seq([
            App.globalPut(self.Variables.sale, Int(1)),
            Approve()
        ])

# owner of property can edit property
    def edit(self):
        Assert(
            Txn.application_args.length() == Int(5),
            Txn.sender() == App.globalGet(self.Variables.owner),
        ),
        Assert(
            Or(
              Txn.sender() == App.globalGet(self.Variables.owner),
              Txn.sender() == self.admin 
            )
        )
        return Seq([
            App.globalPut(self.Variables.image, Txn.application_args[1]),
            App.globalPut(self.Variables.description, Txn.application_args[2]),
            App.globalPut(self.Variables.location, Txn.application_args[3]),
            App.globalPut(self.Variables.sellprice, Txn.application_args[4]),
            Approve()
        ])

    # owner of property can delete property

    def application_deletion(self):
        return Return(Txn.sender() == Global.creator_address())

    # Check transaction conditions
    def application_start(self):
        return Cond(
            [Txn.application_id() == Int(0), self.application_creation()],
            [Txn.on_completion() == OnComplete.DeleteApplication,
             self.application_deletion()],
            [Txn.application_args[0] == self.AppMethods.like, self.like()],
            [Txn.application_args[0] == self.AppMethods.buy, self.buy()],
            [Txn.application_args[0] == self.AppMethods.sell, self.sell()],
            [Txn.application_args[0] == self.AppMethods.edit, self.edit()],
        )

    # The approval program is responsible for processing all application calls to the contract.
    def approval_program(self):
        return self.application_start()

    # The clear program is used to handle accounts using the clear call to remove the smart contract from their balance record.
    def clear_program(self):
        return Return(Int(1))
