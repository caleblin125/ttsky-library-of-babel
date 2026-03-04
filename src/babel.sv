
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

    always_comb begin : randgen //16 bit random-esque function
        if(setSeed)begin
            nextState = {state[10:5]+1'b1, charIn, state[15:11]} ^ (state << 2);
        end else begin
            nextState = (state ^ {state[3:0], state[15:12], state[11:8], state[7:4]}) + {state[7:3], state[7:3], state[15:14], 4'b1101};
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