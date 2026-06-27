-- Profiles table linked to auth.users
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Strategies table
CREATE TABLE IF NOT EXISTS strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    ticker TEXT NOT NULL,
    buy_rule TEXT NOT NULL CHECK (buy_rule IN ('price_above_sma', 'sma_crossover')),
    sell_rule TEXT NOT NULL CHECK (sell_rule IN ('price_below_sma', 'sma_crossover')),
    short_sma_period INTEGER NOT NULL CHECK (short_sma_period > 0),
    long_sma_period INTEGER NOT NULL CHECK (long_sma_period > 0),
    starting_cash NUMERIC NOT NULL CHECK (starting_cash > 0),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (long_sma_period > short_sma_period),
    CHECK (end_date > start_date)
);

-- Backtests table
CREATE TABLE IF NOT EXISTS backtests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL,
    ticker TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    starting_cash NUMERIC NOT NULL,
    final_value NUMERIC NOT NULL,
    total_return_pct NUMERIC NOT NULL,
    num_trades INTEGER NOT NULL DEFAULT 0,
    win_rate NUMERIC,
    max_drawdown_pct NUMERIC,
    config JSONB NOT NULL,
    equity_curve JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Trades table
CREATE TABLE IF NOT EXISTS trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backtest_id UUID NOT NULL REFERENCES backtests(id) ON DELETE CASCADE,
    trade_type TEXT NOT NULL CHECK (trade_type IN ('buy', 'sell')),
    trade_date DATE NOT NULL,
    price NUMERIC NOT NULL,
    shares NUMERIC NOT NULL,
    portfolio_value NUMERIC NOT NULL,
    pnl NUMERIC
);

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email)
    VALUES (NEW.id, NEW.email);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Updated_at trigger for strategies
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS strategies_updated_at ON strategies;
CREATE TRIGGER strategies_updated_at
    BEFORE UPDATE ON strategies
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE backtests ENABLE ROW LEVEL SECURITY;
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- Strategies policies
CREATE POLICY "Users can view own strategies" ON strategies
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own strategies" ON strategies
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own strategies" ON strategies
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own strategies" ON strategies
    FOR DELETE USING (auth.uid() = user_id);

-- Backtests policies
CREATE POLICY "Users can view own backtests" ON backtests
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own backtests" ON backtests
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own backtests" ON backtests
    FOR DELETE USING (auth.uid() = user_id);

-- Trades policies (via backtest ownership)
CREATE POLICY "Users can view own trades" ON trades
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM backtests
            WHERE backtests.id = trades.backtest_id
            AND backtests.user_id = auth.uid()
        )
    );
CREATE POLICY "Users can insert own trades" ON trades
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM backtests
            WHERE backtests.id = trades.backtest_id
            AND backtests.user_id = auth.uid()
        )
    );
