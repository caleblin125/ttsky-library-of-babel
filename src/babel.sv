
module babel(
    input clk,
    input reset,
    input [4:0] charIn, //32 bit: [a-z][ .,!?;]
    input setSeed,
    output [4:0] charOut, //32 bit: [a-z][ .,!?;]
    output isWriting
);
    logic [7:0] counter;
    logic [15:0] state;
    logic [15:0] nextState;

    logic [15:7] shift3;
    assign shift3 = state << 7;
    always_comb begin : randgen //5 bit xorshift
        if(setSeed)begin
            nextState = {state[15:5], charIn} ^ (state << 2);
        end else begin
            nextState = (state ^ {state[14:2], shift3, state[5:1]}) - shift3 + 1;
        end
    end

    logic pageGo;
    assign pageGo = (counter != 8'hFF);
    always @(posedge clk) begin : registers
        if(!reset)begin
            state <= 0;
            counter <= 0;
        end else if(pageGo) begin
            state <= nextState;
            if(!setSeed) begin
                counter <= counter + 1;
            end
        end
    end

    assign isWriting = pageGo;
    assign charOut = pageGo ? state[15:11] : 0;

endmodule